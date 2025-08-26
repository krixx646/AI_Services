"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.conf import settings



urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API namespaces
    path('api/accounts/', include('accounts.urls')),
    path('api/blog/', include('blog.urls')),
    path('api/bots/', include('bots.urls')),
    path('api/demo/', include('demo.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/processing/', include('processing.urls')),

    # API schema and docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Site routes (templates)
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('blog/', TemplateView.as_view(template_name='blog/list.html'), name='blog_list'),
    path('blog/<slug:slug>/', TemplateView.as_view(template_name='blog/detail.html'), name='blog_detail'),
]
