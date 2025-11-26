from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from django.conf import settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from langchain_community.vectorstores import FAISS
from .models import Pergunta, DataTreinamento
import textwrap
import re
from abc import abstractmethod
from langchain_core.prompts import ChatPromptTemplate
from prompts.prompts import SUMMARY_PROMPT, PSI_PROMPT, EVALUATION_PROMPT
from pydantic import BaseModel, Field


class BaseAgent:
    llm = ChatOpenAI(
        model_name='gpt-4.1-mini',
        temperature=0.7,
        openai_api_key=settings.OPENAI_API_KEY
    )
    language: str = 'pt-br'
    audience: str = 'Psicologos e pacientes'

    @abstractmethod
    def _prompt(self): ...

    @abstractmethod
    def run(self): ...


class Summaries(BaseModel):
    summaries: list[str] = Field(description='A lista de resumos')


class SummaryAgent(BaseAgent):

    def _prompt(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                ('system', SUMMARY_PROMPT),
                ('system', PSI_PROMPT),
                ('human',
                 'language: {language} | audience: {audience}\n\nUse a transcricao abaixo: {transcription}')
            ]
        )
        return prompt

    def run(self, transcription):
        chain = self._prompt() | self.llm.with_structured_output(Summaries)
        return chain.invoke({'transcription': transcription, 'language': self.language, 'audience': self.audience})


class Evaluation(BaseModel):
    evaluation: int = Field(
        description='Avaliação de 1 a 5 referente ao humor do paciente com base na transcrição')


class EvaluationAgent(BaseAgent):
    def _prompt(self):
        prompt = ChatPromptTemplate.from_messages([
            ('system', EVALUATION_PROMPT),
            ('human', 'language: {language} | audience: {audience}\nUse a transcrição abaixo: {transcription}')])

        return prompt

    def run(self, transcription):
        chain = self._prompt() | self.llm.with_structured_output(Evaluation)
        return chain.invoke({'transcription': transcription, 'language': self.language, 'audience': self.audience})


class RAGContext:
    def __init__(
        self, db_path='faiss_banco/faiss', chunk_size=500, chunk_overlap=100
    ):
        self.db_path = db_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )

        self.chat = ChatOpenAI(
            model_name='gpt-4.1-mini',
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )

    def train(self, docs, paciente_id):
        chunks = self.splitter.split_documents(docs)
        db_path = f'{self.db_path}_{paciente_id}'
        if os.path.exists(db_path):
            vectordb = FAISS.load_local(
                db_path,  self.embeddings, allow_dangerous_deserialization=True)
            vectordb.add_documents(chunks)
        else:
            vectordb = FAISS.from_documents(chunks,  self.embeddings)
        vectordb.save_local(db_path)

        return vectordb

    def retrieval(self, id_pergunta, id_paciente, k=5):
        pergunta = Pergunta.objects.get(id=id_pergunta)
        db_path = f'{self.db_path}_{id_paciente}'
        vectordb = FAISS.load_local(
            db_path, self.embeddings, allow_dangerous_deserialization=True)

        date = self._extract_date_from_question(pergunta.pergunta)
        if date:
            docs = vectordb.similarity_search(
                pergunta.pergunta, max(k*5, 20), filter={'date': date})
        else:
            docs = vectordb.similarity_search(pergunta.pergunta, k)

        for doc in docs:
            data = DataTreinamento(
                recording_id=doc.metadata['id_recording'],
                text=doc.page_content
            )
            data.save()
            pergunta.data_treinamento.add(data)

        contexto = '\n\n'.join([
            f'Material: {doc.page_content}'
            for doc in docs
        ])

        header = 'Transcrições recuperadas do paciente'
        if date:
            header += f' - Sessão do dia {date}'

        system_prompt = textwrap.dedent(f"""
            Você é um assistente de um psicólogo com acesso a transcrições de consultas.
            Responda APENAS com base no CONTEXTO a seguir. Caso a pergunta especifique uma data,
            considere somente os trechos referentes àquela sessão. Se a informação não estiver no contexto,
            diga explicitamente que não encontrou e não invente dados.

            Regras:
            - Seja direto e profissional.
            - Se houver múltiplos trechos, sintetize sem repetir verbatim.
            - Se a pergunta pedir "o que foi dito", traga pontos objetivos (tópicos).
            - Se a pergunta pedir "resumo" ou "síntese", apresente bullets concisos.
            - Não exponha dados sensíveis como nomes/endereços que não estejam no contexto abaixo.
            - Caso o contexto esteja vazio, diga que não há material correspondente.

            {header}:
            ---
            {contexto or "∅ (sem resultados)"}
            ---
        """).strip()
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f'{pergunta.pergunta}'}
        ]

        for chunk in self.chat.stream(messages):
            token = chunk.content
            if token:
                yield token

    def _extract_date_from_question(self, pergunta):
        # Qual a queixa principal do paciente na consulta do dia 00/00/0000?
        # 00/00/0000
        # 0000-00-00

        m = re.search(r'\b\d{1,2}/\d{1,2}(?:/\d{4})?\b', pergunta)
        if m:
            return m.group(0)

        m2 = re.search(r'\b\d{4}-\d{2}-\d{2}\b', pergunta)
        if m2:
            return m2.group(0)

        return 0
