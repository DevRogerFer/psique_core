from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from usuarios.models import Pacientes
from .models import Gravacoes, Pergunta
from django.urls import reverse
from .agents import RAGContext
from django.views.decorators.csrf import csrf_exempt


def consultas(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    if request.method == 'GET':
        gravacoes = Gravacoes.objects.filter(paciente__id=id).order_by('data')
        return render(
            request,
            'consultas.html',
            {'paciente': paciente, 'gravacoes': gravacoes},
        )
    elif request.method == 'POST':
        gravacao = request.FILES.get('gravacao')
        data = request.POST.get('data')
        trascript = request.POST.get('transcript') == 'on'

        gravacao = Gravacoes(
            video=gravacao, data=data, transcrever=trascript, paciente=paciente
        )

        gravacao.save()

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
