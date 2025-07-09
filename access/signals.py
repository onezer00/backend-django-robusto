from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ChatAccessRequest
from .utils.email_utils import notificar_admin, confirmar_solicitante

@receiver(post_save, sender=ChatAccessRequest)
def enviar_emails_quando_criado(sender, instance, created, **kwargs):
    if created:
        notificar_admin(instance)
        confirmar_solicitante(instance)
