from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio_index, name='portfolio-index'),
    path('projects/', views.projects_list, name='portfolio-projects'),
]


