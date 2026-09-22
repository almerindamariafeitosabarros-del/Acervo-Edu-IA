from django.urls import path

from .views import (
    ModerationDecisionView,
    ModerationQueueView,
    MuralAttachmentFileView,
    MuralCommentListView,
    MuralPostDetailView,
    MuralPostListCreateView,
    MuralReportCreateView,
)

urlpatterns = [
    path('posts/', MuralPostListCreateView.as_view(), name='mural-posts'),
    path('posts/<int:pk>/', MuralPostDetailView.as_view(), name='mural-post-detail'),
    path('posts/<int:post_id>/comments/', MuralCommentListView.as_view(), name='mural-post-comments'),
    path('posts/<int:post_id>/report/', MuralReportCreateView.as_view(), name='mural-post-report'),
    path('attachments/<int:pk>/file/', MuralAttachmentFileView.as_view(), name='mural-attachment-file'),
    path('moderation/', ModerationQueueView.as_view(), name='mural-moderation-queue'),
    path(
        'moderation/<int:post_id>/decidir/',
        ModerationDecisionView.as_view(),
        name='mural-moderation-decision',
    ),
]
