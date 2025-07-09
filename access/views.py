from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework import filters
from .models import ChatAccessRequest
from .serializers import ChatAccessRequestSerializer, ChatAccessRequestStatusSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ChatAccessRequestCreateView(CreateAPIView):
    queryset = ChatAccessRequest.objects.all()
    serializer_class = ChatAccessRequestSerializer

class ChatAccessRequestListView(ListAPIView):
    queryset = ChatAccessRequest.objects.all()
    serializer_class = ChatAccessRequestSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['email', 'nome']
    ordering_fields = ['criado_em', 'status']

    def get_queryset(self):
        queryset = super().get_queryset()
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'status', openapi.IN_QUERY, description="Filtrar por status",
                type=openapi.TYPE_STRING, enum=['pendente', 'aprovado', 'recusado']
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
class ChatAccessRequestStatusUpdateView(UpdateAPIView):
    queryset = ChatAccessRequest.objects.all()
    serializer_class = ChatAccessRequestStatusSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'pk'