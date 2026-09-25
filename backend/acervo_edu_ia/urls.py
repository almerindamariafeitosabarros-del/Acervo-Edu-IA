"""Rotas da API do Acervo Edu IA."""

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.academics.views import (
    CategoryViewSet,
    CourseViewSet,
    InstitutionViewSet,
    SubjectViewSet,
    TagViewSet,
)
from apps.accounts.views import UserViewSet
from apps.documents.views import (
    AllDocumentListView,
    DocumentDetailViewSet,
    DocumentStatsView,
    MyDocumentViewSet,
    PublicDocumentListView,
)

router = DefaultRouter()
router.register('institutions', InstitutionViewSet, basename='institution')
router.register('courses', CourseViewSet, basename='course')
router.register('subjects', SubjectViewSet, basename='subject')
router.register('categories', CategoryViewSet, basename='category')
router.register('tags', TagViewSet, basename='tag')
router.register('users', UserViewSet, basename='user')
router.register('documents/mine', MyDocumentViewSet, basename='my-document')
router.register('documents', DocumentDetailViewSet, basename='document')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/ai/', include('apps.ai.urls')),
    path('api/documents/public/', PublicDocumentListView.as_view(), name='document-public'),
    path('api/documents/all/', AllDocumentListView.as_view(), name='document-all'),
    path('api/documents/stats/', DocumentStatsView.as_view(), name='document-stats'),
    path('api/', include(router.urls)),
]
