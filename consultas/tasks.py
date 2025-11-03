from openai import OpenAI
from django.shortcuts import get_object_or_404
from .models import Gravacoes
from django.conf import settings


def transcribe_recording(id_recording):
    recording = get_object_or_404(Gravacoes, id=id_recording)
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    with open(recording.video.path, 'rb') as f:
        transcription = client.audio.transcriptions.create(
            model='whisper-1',
            file=f,
            response_format='verbose_json',
            language='pt'
        )

        recording.transcricao = transcription.text

        segmentos = []
        for segment in transcription.segments:
            segmentos.append({
                'inicio': segment.start,
                'fim': segment.end,
                'texto': segment.text
            })

        recording.segmentos = segmentos
        recording.save()
        return 'OK'
