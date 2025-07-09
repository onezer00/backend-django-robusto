from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ChatAccessRequest
from .utils.email_utils import confirmar_solicitante, notificar_admin


@receiver(post_save, sender=ChatAccessRequest)
def enviar_emails_quando_criado(sender, instance, created, **kwargs):
    if created:
        notificar_admin(instance)
        confirmar_solicitante(instance)
