from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task(queue="emails")
def enviar_email_async(assunto, mensagem, destinatarios):
    send_mail(
        assunto,
        mensagem,
        settings.DEFAULT_FROM_EMAIL,
        destinatarios,
        fail_silently=False,
    )
