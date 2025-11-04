from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from usuarios.models import Pacientes
from .models import Gravacoes
from django.urls import reverse


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
