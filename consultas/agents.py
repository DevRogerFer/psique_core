from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from django.conf import settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from langchain_community.vectorstores import FAISS


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
