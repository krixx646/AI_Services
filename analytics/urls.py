from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_dashboard, name='analytics_dashboard'),
    path('exclude/', views.exclude_from_analytics, name='exclude_analytics'),
]
