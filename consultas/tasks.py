from openai import OpenAI
from django.shortcuts import get_object_or_404
from .models import Gravacoes
from django.conf import settings
from langchain_core.documents import Document
from .agents import RAGContext, SummaryAgent, EvaluationAgent


def transcribe_recording(id_recording):
    import logging
    logger = logging.getLogger(__name__)

    try:
        recording = get_object_or_404(Gravacoes, id=id_recording)
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # Usar URL do Cloudinary ao invés de path local
        video_url = recording.video.url if hasattr(
            recording.video, 'url') else None

        if not video_url:
            raise ValueError(
                f"URL do vídeo não disponível para gravação {id_recording}")

        logger.info(f"Baixando vídeo de {video_url}")
        # Baixar arquivo do Cloudinary
        import requests
        response = requests.get(video_url)
        if response.status_code != 200:
            raise ValueError(f"Erro ao baixar vídeo: {response.status_code}")

        logger.info(f"Vídeo baixado com sucesso. Enviando para transcrição...")

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
        logger.info(
            f"Transcrição concluída com sucesso para gravacao {id_recording}")
        return 'OK'

    except Exception as e:
        logger.error(
            f"Erro ao transcrever gravação {id_recording}: {str(e)}", exc_info=True)
        return f"ERRO: {str(e)}"


def task_rag(id_recording):
    import logging
    logger = logging.getLogger(__name__)

    try:
        recording = get_object_or_404(Gravacoes, id=id_recording)

        if not recording.transcricao:
            logger.warning(
                f"Gravacao {id_recording} sem transcrição. Pulando RAG.")
            return "SEM_TRANSCRICAO"

        if not recording.data:
            logger.warning(
                f"Gravacao {id_recording} sem data. Usando data atual.")
            from django.utils import timezone
            data_str = timezone.now().strftime("%d/%m/%Y")
        else:
            data_str = recording.data.strftime("%d/%m/%Y")

        docs = [Document(page_content=recording.transcricao, metadata={
                         "date": data_str, 'id_recording': id_recording}),]
        RAGContext().train(docs, recording.paciente.id)
        logger.info(f"RAG treinado com sucesso para gravacao {id_recording}")
        return "OK"

    except Exception as e:
        logger.error(
            f"Erro ao processar RAG para gravacao {id_recording}: {str(e)}", exc_info=True)
        return f"ERRO: {str(e)}"


def summary_recording(id_recording):
    import logging
    logger = logging.getLogger(__name__)

    try:
        recording = get_object_or_404(Gravacoes, id=id_recording)

        if not recording.transcricao:
            logger.warning(
                f"Gravacao {id_recording} sem transcrição. Pulando resumo.")
            return "SEM_TRANSCRICAO"

        logger.info(f"Gerando resumo para gravacao {id_recording}")
        summary_result = SummaryAgent().run(transcription=recording.transcricao)
        recording.resumo = summary_result.summaries

        logger.info(f"Gerando avaliação de humor para gravacao {id_recording}")
        evaluation_result = EvaluationAgent().run(transcription=recording.transcricao)
        recording.humor = evaluation_result.evaluation

        recording.save()
        logger.info(
            f"Resumo e humor salvos com sucesso para gravacao {id_recording}")
        return "OK"

    except Exception as e:
        logger.error(
            f"Erro ao gerar resumo para gravacao {id_recording}: {str(e)}", exc_info=True)
        return f"ERRO: {str(e)}"
