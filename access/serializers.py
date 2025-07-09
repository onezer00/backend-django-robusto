from rest_framework import serializers
from .models import ChatAccessRequest

class ChatAccessRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatAccessRequest
        fields = ['id', 'nome', 'email', 'motivo', 'criado_em', 'status']
        read_only_fields = ['id', 'criado_em', 'status']
        
    def validate_email(self, value):
        existing_request = ChatAccessRequest.objects.filter(email=value).order_by('-criado_em').first()
        if existing_request:
            status = existing_request.status
            if status == 'pendente':
                raise serializers.ValidationError("Já existe uma solicitação pendente para este e-mail.")
            elif status == 'aprovado':
                raise serializers.ValidationError("Este e-mail já foi aprovado. Você já tem acesso.")
            elif status == 'recusado':
                raise serializers.ValidationError("Este e-mail já foi recusado. Entre em contato com o suporte.")
        return value


class ChatAccessRequestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatAccessRequest
        fields = ['status']