from django.urls import path

from .views import AIStatusView, AskView, HistoryView

urlpatterns = [
    path('ask/', AskView.as_view(), name='ai-ask'),
    path('history/', HistoryView.as_view(), name='ai-history'),
    path('status/', AIStatusView.as_view(), name='ai-status'),
]
