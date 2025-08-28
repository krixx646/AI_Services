from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('posts', views.PostViewSet, basename='posts')
router.register('categories', views.CategoryViewSet, basename='categories')
router.register('tags', views.TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    path('posts/<int:post_id>/comments/', views.PostCommentsView.as_view(), name='post-comments'),
    path('comments/<int:comment_id>/moderate/', views.CommentModerateView.as_view(), name='comment-moderate'),
    path('comments/<int:comment_id>/', views.CommentDetailView.as_view(), name='comment-detail'),
]
