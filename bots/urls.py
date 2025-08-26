from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('reviews', views.ReviewViewSet, basename='reviews')

urlpatterns = [
    path('<uuid:reference>/questions/', views.QuestionsView.as_view(), name='bot-questions'),
    path('<uuid:reference>/answer/', views.AnswerView.as_view(), name='bot-answer'),
    path('', include(router.urls)),
]
