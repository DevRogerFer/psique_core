import time
import re
from .wrapper_cloudapi import WhatsAppCloudAPI
from .models import Gravacoes
import logging
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from usuarios.models import Pacientes
from .models import Gravacoes, Pergunta, DataTreinamento
from django.urls import reverse
from .agents import RAGContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.humanize.templatetags.humanize import naturaltime
from datetime import datetime
# from .wrapper_evolutionapi import BaseEvolutionAPI, SendMessage


def consultas(request, id):
    paciente = get_object_or_404(Pacientes, id=id)

    # ---------------------------------------------------------------------
    # GET → Exibe a página da consulta (sem enviar mensagens)
    # ---------------------------------------------------------------------
    if request.method == 'GET':

        gravacoes = Gravacoes.objects.filter(paciente_id=id).order_by("data")

        # Corrige o problema do datetime vs string
        datas = [
            g.data.date() if hasattr(g.data, "date") else g.data
            for g in gravacoes
        ]

        humores = [g.humor for g in gravacoes]

        return render(
            request,
            'consultas.html',
            {
                'paciente': paciente,
                'gravacoes': gravacoes,
                'datas': datas,
                'humores': humores,
            }
        )

    # ---------------------------------------------------------------------
    # POST → Salva nova gravação
    # ---------------------------------------------------------------------
    elif request.method == 'POST':
        from django.utils import timezone
        from datetime import datetime

        gravacao_file = request.FILES.get("gravacao")
        data_str = request.POST.get("data")
        transcript = request.POST.get("transcript") == "on"

        # Converter string de data para datetime
        try:
            if data_str:
                data = datetime.strptime(data_str, "%Y-%m-%d")
                data = timezone.make_aware(data)
            else:
                data = timezone.now()
        except (ValueError, TypeError):
            data = timezone.now()

        gravacao = Gravacoes(
            video=gravacao_file,
            data=data,
            transcrever=transcript,
            paciente=paciente
        )

        try:
            gravacao.save()
            messages.success(request, "Gravação salva com sucesso!")
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao salvar gravacao: {str(e)}")
            messages.error(
                request, "Erro ao salvar gravação. Tente novamente.")

        return redirect(reverse('consultas', kwargs={'id': id}))


@csrf_exempt
def stream_response(request, id):
    id_pergunta = request.POST.get('id_pergunta')
    return StreamingHttpResponse(RAGContext().retrieval(id_pergunta, id))


@csrf_exempt
def chat(request, id):
    if request.method == 'GET':
        paciente = get_object_or_404(Pacientes, id=id)
        return render(request, 'chat.html', {'paciente': paciente})
    elif request.method == 'POST':
        pergunta_user = request.POST.get('pergunta')
        pergunta = Pergunta(
            pergunta=pergunta_user
        )
        pergunta.save()

        return JsonResponse({'id': pergunta.id})


def gravacao(request, id):
    gravacao = get_object_or_404(Gravacoes, id=id)
    return render(request, 'gravacao.html', {'gravacao': gravacao})


def ver_referencias(request, id):
    pergunta = get_object_or_404(Pergunta, id=id)
    data_treinamento = pergunta.data_treinamento.all()
    gravacoes = Gravacoes.objects.filter(
        datatreinamento__in=data_treinamento).distinct()

    return render(request, 'ver_referencias.html', {'pergunta': pergunta, 'data_treinamento': data_treinamento, 'gravacoes': gravacoes})


logger = logging.getLogger("whatsapp")


def send_message(request, id):
    gravacao = get_object_or_404(Gravacoes, id=id)
    telefone = gravacao.paciente.telefone.strip()

    # Validação do telefone
    if not re.match(r"^55\d{10,11}$", telefone):
        messages.error(request, "Telefone inválido.")
        logger.error(f"Telefone inválido: {telefone}")
        return redirect(f'/consultas/gravacao/{id}')

    # Instância API
    api = WhatsAppCloudAPI()

    # Envio das mensagens da gravação (texto simples)
    for texto in gravacao.resumo:
        logger.debug(f"Enviando resumo para {telefone}: {texto}")

        resp_json, status = api.send_text(telefone, texto)

        if status >= 400:
            logger.error(f"Erro ao enviar texto: {status} | {resp_json}")
        else:
            logger.info(f"Texto enviado com sucesso → {telefone}")

    messages.success(request, "Resumo enviado com sucesso!")
    return redirect(f'/consultas/gravacao/{id}')
