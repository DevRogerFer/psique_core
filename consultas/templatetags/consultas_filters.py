from django import template
from ..models import Gravacoes

register = template.Library()


@register.filter
def count_words(text):
    return len(text.split())


@register.filter
def tempo_video(trecho, gravacao_id):
    trecho = trecho.lower().strip()
    gravacao = Gravacoes.objects.get(id=gravacao_id)
    for segmento in gravacao.segmentos:
        seg = segmento.get('texto', '').lower().strip()
        if seg in trecho or trecho in seg:
            return segmento.get('inicio')
