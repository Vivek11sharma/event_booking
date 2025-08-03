# payments/urls.py
from django.urls import path
from .views import StripeWebhookView, payment_success, payment_cancel

urlpatterns = [
    path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('success/', payment_success, name='payment-success'),
    path('cancel/', payment_cancel, name='payment-cancel'),
]
