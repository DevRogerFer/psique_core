from django.db import models


class Pacientes(models.Model):
    nome = models.CharField(max_length=64)
    descricao = models.TextField()
    foto = models.ImageField(upload_to='fotos')
    ativo = models.BooleanField(default=True)
    telefone = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.nome
