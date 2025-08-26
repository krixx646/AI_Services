from django.urls import path
from . import views

urlpatterns = [
    path('info/', views.DemoInfoView.as_view(), name='demo-info'),
]
