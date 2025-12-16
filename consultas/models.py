from django.db import models
from usuarios.models import Pacientes


class Gravacoes(models.Model):
    video = models.FileField(
        upload_to="gravacoes/",
        blank=True,
        null=True
    )
    data = models.DateTimeField(auto_now_add=True)
    transcrever = models.BooleanField(default=False)
    paciente = models.ForeignKey(Pacientes, on_delete=models.DO_NOTHING)
    humor = models.IntegerField(default=0)
    transcricao = models.TextField()
    resumo = models.JSONField(default=list, blank=True)
    segmentos = models.JSONField(default=list, blank=True)


class DataTreinamento(models.Model):
    recording = models.ForeignKey(Gravacoes, on_delete=models.DO_NOTHING)
    text = models.TextField()


class Pergunta(models.Model):
    data_treinamento = models.ManyToManyField(
        DataTreinamento,
        blank=True
    )
    pergunta = models.TextField()

    def __str__(self):
        return self.pergunta
