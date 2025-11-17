from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Gravacoes
from .tasks import transcribe_recording, task_rag, summary_recording
from django_q.tasks import async_task, Chain


@receiver(post_save, sender=Gravacoes)
def signals_gravacoes_transcricao_resumos(sender, instance, created, **kwargs):
    if created:
        if instance.transcrever:
            chain = Chain()
            chain.append(transcribe_recording, instance.id)
            chain.append(task_rag, instance.id)
            chain.append(summary_recording, instance.id)
            chain.run()
