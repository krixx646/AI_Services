from django.urls import path, include
from django.http import JsonResponse
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('register', views.RegistrationViewSet, basename='register')
router.register('login', views.LoginViewSet, basename='login')
router.register('profile', views.ProfileViewSet, basename='profile')



def health(request):
    return JsonResponse({"ok": True})

urlpatterns = [
    path("health/", health, name="health"),
    path("verify-email/", views.verify_email_view, name="verify_email"),
    path('', include(router.urls)),

]