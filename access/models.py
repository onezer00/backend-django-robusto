from django.db import models


class ChatAccessRequest(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    motivo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pendente", "Pendente"),
            ("aprovado", "Aprovado"),
            ("recusado", "Recusado"),
        ],
        default="pendente",
    )

    def __str__(self):
        return f"{self.nome} ({self.status})"
