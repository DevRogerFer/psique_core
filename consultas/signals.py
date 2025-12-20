from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Gravacoes
from .tasks import transcribe_recording
from django_q.tasks import async_task
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
                    f"Iniciando processamento para gravacao {instance.id}")
                # Disparar task de transcrição
                async_task(transcribe_recording, instance.id)
                logger.info(
                    f"Task de transcrição disparada para gravacao {instance.id}")
            except Exception as e:
                logger.error(
                    f"Erro ao disparar task para gravacao {instance.id}: {str(e)}", exc_info=True)
        else:
            logger.info(f"Gravacao {instance.id} não marcada para transcrição")
