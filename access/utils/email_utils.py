from access.tasks import enviar_email_async
from django.conf import settings

def notificar_admin(nova_requisicao):
    assunto = "Nova solicitação de acesso ao chat"
    mensagem = (
        f'Nova solicitação de acesso ao chat recebida:\n\n'
        f'Nome: {nova_requisicao.nome}\n'
        f'Email: {nova_requisicao.email}\n'
        f'Motivo: {nova_requisicao.motivo}\n\n'
        f'Acesse o admin para aprovar ou recusar: {settings.ADMIN_BASE_URL}/access/chataccessrequest/{nova_requisicao.id}/change/'
    )
    enviar_email_async.delay(
        assunto,
        mensagem,
        [settings.DEFAULT_FROM_EMAIL]
    )

def confirmar_solicitante(nova_requisicao):
    assunto = 'Recebemos sua solicitação de acesso ao chat'
    mensagem = (
        f'Olá {nova_requisicao.nome},\n\n'
        'Recebemos sua solicitação de acesso ao chat e ela será analisada em breve.\n\n'
        'Você receberá uma resposta por e-mail após a aprovação ou recusa.\n\n'
        'Atenciosamente,\nEquipe'
    )
    enviar_email_async.delay(
        assunto,
        mensagem,
        [nova_requisicao.email]
    )

def informar_decisao(solicitacao, motivo_recusa=None):
    if solicitacao.status == 'aprovado':
        assunto = 'Sua solicitação foi aprovada!'
        mensagem = (
            f'Olá {solicitacao.nome},\n\n'
            'Sua solicitação de acesso ao chat foi aprovada!\n\n'
            f'Acesse agora: {settings.CHAT_BASE_URL}\n\n'
            'Atenciosamente,\nEquipe'
        )
    else:
        assunto = 'Sua solicitação foi recusada'
        mensagem = (
            f'Olá {solicitacao.nome},\n\n'
            'Infelizmente sua solicitação de acesso ao chat foi recusada.\n'
            f'Motivo: {motivo_recusa or "Não especificado"}\n\n'
            'Atenciosamente,\nEquipe'
        )

    enviar_email_async.delay(
        assunto,
        mensagem,
        [solicitacao.email]
    )

