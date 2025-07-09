from django.urls import path

from .views import (
    ChatAccessRequestCreateView,
    ChatAccessRequestListView,
    ChatAccessRequestStatusUpdateView,
)

urlpatterns = [
    path(
        "chat-access-request/",
        ChatAccessRequestCreateView.as_view(),
        name="chat-access-request",
    ),
    path(
        "chat-access-request/list/",
        ChatAccessRequestListView.as_view(),
        name="chat-access-request-list",
    ),
    path(
        "chat-access-request/<int:pk>/status/",
        ChatAccessRequestStatusUpdateView.as_view(),
        name="chat-access-request-status",
    ),
]
