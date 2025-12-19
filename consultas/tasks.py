from openai import OpenAI
from django.shortcuts import get_object_or_404
from .models import Gravacoes
from django.conf import settings
from langchain_core.documents import Document
from .agents import RAGContext, SummaryAgent, EvaluationAgent


def transcribe_recording(id_recording):
    recording = get_object_or_404(Gravacoes, id=id_recording)
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    try:
        # Usar URL do Cloudinary ao invés de path local
        video_url = recording.video.url if hasattr(
            recording.video, 'url') else None

        if not video_url:
            raise ValueError(
                f"URL do vídeo não disponível para gravação {id_recording}")

        # Baixar arquivo do Cloudinary
        import requests
        response = requests.get(video_url)
        if response.status_code != 200:
            raise ValueError(f"Erro ao baixar vídeo: {response.status_code}")

        # Enviar para OpenAI Whisper usando bytes
        from io import BytesIO
        audio_file = BytesIO(response.content)
        audio_file.name = f"gravacao_{id_recording}.mp4"

        transcription = client.audio.transcriptions.create(
            model='whisper-1',
            file=audio_file,
            response_format='verbose_json',
            language='pt',
        )

        recording.transcricao = transcription.text

        segmentos = []
        for segment in transcription.segments:
            segmentos.append(
                {
                    'inicio': segment.start,
                    'fim': segment.end,
                    'texto': segment.text,
                }
            )

        recording.segmentos = segmentos
        recording.save()
        return 'OK'

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao transcrever gravação {id_recording}: {str(e)}")
        return f"ERRO: {str(e)}"


def task_rag(id_recording):
    recording = get_object_or_404(Gravacoes, id=id_recording)

    docs = [Document(page_content=recording.transcricao, metadata={
                     "date": recording.data.strftime("%d/%m/%Y"), 'id_recording': id_recording}),]
    RAGContext().train(docs, recording.paciente.id)


def summary_recording(id_recording):
    recording = get_object_or_404(Gravacoes, id=id_recording)
    recording.resumo = SummaryAgent().run(
        transcription=recording.transcricao).summaries
    recording.humor = EvaluationAgent().run(
        transcription=recording.transcricao).evaluation
    recording.save()
