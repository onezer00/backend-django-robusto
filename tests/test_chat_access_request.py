from unittest.mock import Mock

import pytest
from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test.client import RequestFactory
from django.urls import reverse
from rest_framework.request import Request
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from access.admin import ChatAccessRequestAdmin
from access.models import ChatAccessRequest
from access.tasks import enviar_email_async
from access.utils.email_utils import notificar_admin
from access.views import ChatAccessRequestListView


@pytest.mark.django_db
class TestChatAccessRequest:

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("chat-access-request")
        self.data = {
            "nome": "João Teste",
            "email": "joao@example.com",
            "motivo": "Gostaria de testar o sistema",
        }

    def _get_mocked_request(self):
        factory = RequestFactory()
        request = factory.get("/")
        # Adiciona suporte ao sistema de mensagens
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        return request

    def test_model_str_representation(self):
        obj = ChatAccessRequest(nome="Maria", status="aprovado")
        assert str(obj) == "Maria (aprovado)"

    def test_notificar_admin(self, mocker):
        mock = mocker.patch("access.utils.email_utils.enviar_email_async.delay")
        requisicao = ChatAccessRequest(nome="Ex", email="a@a.com", motivo="x")
        notificar_admin(requisicao)
        mock.assert_called_once()

    def test_criar_requisicao_sucesso(self, mocker):
        mock_send = mocker.patch("access.utils.email_utils.enviar_email_async.delay")
        response = self.client.post(self.url, self.data, format="json")
        assert response.status_code == 201
        assert ChatAccessRequest.objects.count() == 1

    def test_nao_permite_email_repetido_pendente(self, mocker):
        mocker.patch("access.utils.email_utils.enviar_email_async.delay")
        ChatAccessRequest.objects.create(**self.data)
        response = self.client.post(self.url, self.data, format="json")
        assert response.status_code == 400
        assert "Já existe uma solicitação pendente" in response.data["email"][0]

    def test_nao_permite_email_repetido_aprovado(self, mocker):
        mocker.patch("access.utils.email_utils.enviar_email_async.delay")
        ChatAccessRequest.objects.create(**self.data, status="aprovado")
        response = self.client.post(self.url, self.data, format="json")
        assert response.status_code == 400
        assert "já foi aprovado" in response.data["email"][0]

    def test_nao_permite_email_repetido_recusado(self, mocker):
        mocker.patch("access.utils.email_utils.enviar_email_async.delay")
        ChatAccessRequest.objects.create(**self.data, status="recusado")
        response = self.client.post(self.url, self.data, format="json")
        assert response.status_code == 400
        assert "já foi recusado" in response.data["email"][0]

    def test_emails_enviados_ao_criar(self, mocker):
        mock_send = mocker.patch("access.utils.email_utils.enviar_email_async.delay")
        response = self.client.post(self.url, self.data, format="json")
        assert response.status_code == 201
        assert mock_send.call_count >= 1

    def test_status_colored(self, mocker):
        mocker.patch("access.utils.email_utils.enviar_email_async.delay")
        admin_instance = ChatAccessRequestAdmin(ChatAccessRequest, AdminSite())
        obj = ChatAccessRequest(
            nome="João", email="j@x.com", motivo="X", status="aprovado"
        )
        obj.save()
        html = admin_instance.status_colored(obj)
        assert "green" in html

    def test_has_change_permission(self):
        admin_instance = ChatAccessRequestAdmin(ChatAccessRequest, AdminSite())
        assert admin_instance.has_change_permission(None) is True

    def test_has_add_permission(self):
        admin_instance = ChatAccessRequestAdmin(ChatAccessRequest, AdminSite())
        assert admin_instance.has_add_permission(None) is False

    def test_get_fields(self):
        admin_instance = ChatAccessRequestAdmin(ChatAccessRequest, AdminSite())
        fields = admin_instance.get_fields(None)
        assert fields == ["nome", "email", "motivo", "criado_em", "status"]

    def test_aprovar_requisicoes(self, mocker):
        mocker.patch("access.utils.email_utils.enviar_email_async.delay")
        obj = ChatAccessRequest.objects.create(**self.data)
        admin_instance = ChatAccessRequestAdmin(ChatAccessRequest, AdminSite())
        mock = mocker.patch("access.admin.informar_decisao")
        queryset = ChatAccessRequest.objects.filter(id=obj.id)
        request = self._get_mocked_request()
        admin_instance.aprovar_requisicoes(request, queryset)
        obj.refresh_from_db()
        assert obj.status == "aprovado"
        mock.assert_called_once()

    def test_recusar_requisicoes(self, mocker):
        mocker.patch("access.utils.email_utils.enviar_email_async.delay")
        obj = ChatAccessRequest.objects.create(**self.data)
        admin_instance = ChatAccessRequestAdmin(ChatAccessRequest, AdminSite())
        mock = mocker.patch("access.admin.informar_decisao")
        queryset = ChatAccessRequest.objects.filter(id=obj.id)
        request = self._get_mocked_request()
        admin_instance.recusar_requisicoes(request, queryset)
        obj.refresh_from_db()
        assert obj.status == "recusado"
        mock.assert_called_once()

    def test_informar_decisao_aprovado(self, mocker):
        mock = mocker.patch("access.utils.email_utils.enviar_email_async.delay")
        obj = ChatAccessRequest(
            nome="João", email="joao@example.com", motivo="Teste", status="aprovado"
        )

        from access.utils.email_utils import informar_decisao

        informar_decisao(obj)

        mock.assert_called_once()
        args, kwargs = mock.call_args
        assert "aprovada" in args[1]  # verifica a mensagem
        assert obj.email in args[2]  # verifica destinatário

    def test_informar_decisao_recusado_com_motivo(self, mocker):
        mock = mocker.patch("access.utils.email_utils.enviar_email_async.delay")
        obj = ChatAccessRequest(
            nome="João", email="joao@example.com", motivo="Teste", status="recusado"
        )

        from access.utils.email_utils import informar_decisao

        informar_decisao(obj, motivo_recusa="Não atende os requisitos")

        mock.assert_called_once()
        args, kwargs = mock.call_args
        assert "recusada" in args[1]
        assert "Não atende os requisitos" in args[1]
        assert obj.email in args[2]

    def test_informar_decisao_recusado_sem_motivo(self, mocker):
        mock = mocker.patch("access.utils.email_utils.enviar_email_async.delay")
        obj = ChatAccessRequest(
            nome="João", email="joao@example.com", motivo="Teste", status="recusado"
        )

        from access.utils.email_utils import informar_decisao

        informar_decisao(obj)

        mock.assert_called_once()
        args, kwargs = mock.call_args
        assert "Não especificado" in args[1]
        assert obj.email in args[2]

    def test_get_queryset_com_e_sem_filtro(self, mocker):
        mock = mocker.patch("access.utils.email_utils.enviar_email_async.delay")
        ChatAccessRequest.objects.create(
            nome="Aprovado", email="a@a.com", motivo="x", status="aprovado"
        )
        ChatAccessRequest.objects.create(
            nome="Recusado", email="b@b.com", motivo="y", status="recusado"
        )

        factory = APIRequestFactory()

        # Teste sem filtro de status
        request = factory.get("/fake-url/")
        view = ChatAccessRequestListView()
        view.request = Request(request)

        queryset = view.get_queryset()
        assert queryset.count() == 2

        # Teste com filtro status=aprovado
        request = factory.get("/fake-url/?status=aprovado")
        view.request = Request(request)

        queryset = view.get_queryset()
        assert queryset.count() == 1
        assert queryset.first().status == "aprovado"

        # Teste com filtro status=recusado
        request = factory.get("/fake-url/?status=recusado")
        view.request = Request(request)

        queryset = view.get_queryset()
        assert queryset.count() == 1
        assert queryset.first().status == "recusado"

    def test_save_model_dispara_email_quando_status_muda(self, mocker):
        mocker.patch("access.utils.email_utils.enviar_email_async.delay")
        # Cria uma solicitação inicial no banco (status pendente)
        obj_original = ChatAccessRequest.objects.create(
            nome="João",
            email="joao@example.com",
            motivo="Motivo original",
            status="pendente",
        )

        # Simula alteração para aprovado
        obj_modificado = ChatAccessRequest.objects.get(id=obj_original.id)
        obj_modificado.status = "aprovado"

        # Mocka o método informar_decisao
        mock_informar = mocker.patch("access.admin.informar_decisao")

        # Instancia o admin
        admin_instance = ChatAccessRequestAdmin(ChatAccessRequest, AdminSite())

        # Cria um mock de request do admin
        mock_request = Mock()

        # Executa o método de salvar com mudança
        admin_instance.save_model(mock_request, obj_modificado, form=None, change=True)

        # Verifica se a função de notificação foi chamada
        mock_informar.assert_called_once_with(obj_modificado)

    def test_chat_access_request_list_view_get(self, mocker):
        mocker.patch("access.utils.email_utils.enviar_email_async.delay")
        # Cria um usuário admin
        admin_user = User.objects.create_superuser(
            username="admin", password="admin", email="admin@example.com"
        )

        # Cria dados de teste
        ChatAccessRequest.objects.create(
            nome="Ana", email="ana@example.com", motivo="teste", status="aprovado"
        )
        ChatAccessRequest.objects.create(
            nome="Bruno", email="bruno@example.com", motivo="outro", status="pendente"
        )

        # Cria requisição GET com filtro de status
        factory = APIRequestFactory()
        request = factory.get("/api/access-requests/?status=aprovado")

        # Força autenticação como admin
        force_authenticate(request, user=admin_user)

        # Instancia a view
        view = ChatAccessRequestListView.as_view()

        # Executa a view
        response = view(request)

        # Verifica se retornou corretamente
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["nome"] == "Ana"

    def test_enviar_email_async(self, mocker):
        # mock

        mock_send_mail = mocker.patch("access.tasks.send_mail")

        assunto = "Teste"
        mensagem = "Mensagem de teste"
        destinatarios = ["teste@example.com"]

        enviar_email_async(assunto, mensagem, destinatarios)

        # Checa se o email final foi enviado com o valor real do settings
        actual_args = mock_send_mail.call_args[0]
        assert actual_args[0] == assunto
        assert actual_args[1] == mensagem
        assert actual_args[2] == settings.DEFAULT_FROM_EMAIL
        assert actual_args[3] == destinatarios
        assert mock_send_mail.call_args[1]["fail_silently"] is False
