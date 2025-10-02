from django.urls import path
from . import views

urlpatterns = [
    path('init/', views.InitPaymentView.as_view(), name='payments-init'),
    path('prepare/', views.PreparePaymentView.as_view(), name='payments-prepare'),
    path('webhook/', views.PaystackWebhookView.as_view(), name='payments-webhook'),
    path('verify/<str:reference>/', views.VerifyPaymentView.as_view(), name='payments-verify'),
    path('success/', views.PaymentSuccessPageView.as_view(), name='payment_success'),
    path('receipt/<str:reference>/', views.PaymentReceiptPageView.as_view(), name='payment_receipt'),
    path('force-link-bot/<str:reference>/', views.ForceLinkBotView.as_view(), name='payments-force-link-bot'),
]
