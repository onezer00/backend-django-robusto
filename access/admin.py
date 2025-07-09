from django.contrib import admin
from django.utils.html import format_html

from .models import ChatAccessRequest
from .utils.email_utils import informar_decisao


@admin.register(ChatAccessRequest)
class ChatAccessRequestAdmin(admin.ModelAdmin):
    class Media:
        css = {"all": ("admin/access/admin.css",)}

    list_display = ("nome", "email", "status_colored", "criado_em")
    list_filter = ("status", "criado_em")
    search_fields = ("nome", "email", "motivo")
    readonly_fields = ("nome", "email", "motivo", "criado_em")
    actions = ["aprovar_requisicoes", "recusar_requisicoes"]

    def status_colored(self, obj):
        color = {"pendente": "orange", "aprovado": "green", "recusado": "red"}.get(
            obj.status, "gray"
        )

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_colored.short_description = "Status"

    def save_model(self, request, obj, form, change):
        if change:
            antigo = ChatAccessRequest.objects.get(pk=obj.pk)
            if antigo.status != obj.status:
                # Se quiser, pode capturar motivo da recusa de outro campo futuro aqui
                informar_decisao(obj)
        super().save_model(request, obj, form, change)

    def aprovar_requisicoes(self, request, queryset):
        updated = queryset.update(status="aprovado")
        for req in queryset:
            informar_decisao(req)
        self.message_user(request, f"{updated} requisições aprovadas.")

    aprovar_requisicoes.short_description = "Aprovar requisições selecionadas"

    def recusar_requisicoes(self, request, queryset):
        updated = queryset.update(status="recusado")
        for req in queryset:
            informar_decisao(req)

        self.message_user(request, f"{updated} requisições recusadas.")

    recusar_requisicoes.short_description = "Recusar requisições selecionadas"

    def has_add_permission(self, request):
        return False  # impede adicionar pelo admin (se quiser)

    def has_change_permission(self, request, obj=None):
        return True  # ainda permite mudar status manualmente

    def get_fields(self, request, obj=None):
        return ["nome", "email", "motivo", "criado_em", "status"]
