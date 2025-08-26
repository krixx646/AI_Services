from django.urls import path
from . import views

urlpatterns = [
    path('init/', views.InitPaymentView.as_view(), name='payments-init'),
    path('webhook/', views.PaystackWebhookView.as_view(), name='payments-webhook'),
    path('verify/<str:reference>/', views.VerifyPaymentView.as_view(), name='payments-verify'),
]
