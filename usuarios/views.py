from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib import auth


def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR,
                                 'Senha e confirmar senha não conferem!')
            return redirect('cadastro')

        if len(senha) < 6:
            messages.add_message(request, constants.ERROR,
                                 'Senha deve possuir no mínimo 6 caracteres!')
            return redirect('cadastro')

        if User.objects.filter(username=username).exists():
            messages.add_message(request, constants.ERROR,
                                 'Usuário existente com o mesmo username!')
            return redirect('cadastro')

        User.objects.create_user(
            username=username,
            password=senha
        )

        return redirect('login')


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(request, username=username, password=senha)
        if user:
            auth.login(request, user)
            return redirect('paciente')

        messages.add_message(request, constants.ERROR,
                             'Usuário ou senha inválidos!')
        return redirect('login')
