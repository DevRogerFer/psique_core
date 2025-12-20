from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Gravacoes
from .tasks import transcribe_recording, task_rag, summary_recording
from django_q.tasks import async_task, Chain
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Gravacoes)
def signals_gravacoes_transcricao_resumos(sender, instance, created, **kwargs):
    if created:
        logger.info(
            f"Gravacao criada: ID={instance.id}, transcrever={instance.transcrever}")
        if instance.transcrever:
            try:
                logger.info(
                    f"Iniciando chain de processamento para gravacao {instance.id}")
                # Criar chain com as 3 tasks em sequência
                chain = Chain()
                chain.append(transcribe_recording, instance.id)
                chain.append(task_rag, instance.id)
                chain.append(summary_recording, instance.id)
                # Enfileirar o chain em vez de executar imediatamente
                async_task(chain)
                logger.info(
                    f"Chain de processamento disparado para gravacao {instance.id}")
            except Exception as e:
                logger.error(
                    f"Erro ao disparar chain para gravacao {instance.id}: {str(e)}", exc_info=True)
        else:
            logger.info(f"Gravacao {instance.id} não marcada para transcrição")
