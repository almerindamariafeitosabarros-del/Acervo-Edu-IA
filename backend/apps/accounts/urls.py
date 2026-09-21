from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ChangePasswordView,
    ConsentView,
    DeleteMyAccountView,
    ExportMyDataView,
    LoginView,
    MeView,
    RegisterView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('change-password/', ChangePasswordView.as_view(), name='auth-change-password'),

    # Direitos do titular dos dados (LGPD, art. 18)
    path('me/export/', ExportMyDataView.as_view(), name='auth-export-data'),
    path('me/delete/', DeleteMyAccountView.as_view(), name='auth-delete-account'),
    path('consent/', ConsentView.as_view(), name='auth-consent'),
]
