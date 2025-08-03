# payments/views.py
import stripe
from django.conf import settings
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from bookings.models import Booking
from django.shortcuts import render
from rest_framework.views import APIView
from decimal import Decimal


stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeWebhookView(APIView):
    @method_decorator(csrf_exempt, name='dispatch')
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except (ValueError, stripe.error.SignatureVerificationError):
            return HttpResponse(status=400)

        # Handle payment success: update inventory and booking status
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            payment_intent_id = session.get('payment_intent')

            if payment_intent_id:
                try:
                    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                    booking_id = payment_intent.metadata.get('booking_id')

                    if booking_id:
                        booking = Booking.objects.get(id=booking_id)

                        if booking.status != 'paid':
                            # Deduct ticket quantities
                            for ticket in booking.tickets.all():
                                ticket_type = ticket.ticket_type
                                if ticket_type.quantity >= ticket.quantity:
                                    ticket_type.quantity -= ticket.quantity
                                    ticket_type.save()

                            # Calculate platform fee and organizer revenue
                            platform_percentage = settings.PLATFORM_FEE_PERCENTAGE
                            platform_fee = booking.total_amount * (platform_percentage / Decimal('100'))
                            organizer_revenue = booking.total_amount - platform_fee

                            # Update booking with financial data
                            booking.platform_fee = platform_fee
                            booking.organizer_revenue = organizer_revenue
                            booking.status = 'paid'
                            booking.save()

                except Exception:
                    return HttpResponse(status=404)

        # Handle charge success: save receipt URL
        elif event['type'] == 'charge.succeeded':
            charge = event['data']['object']
            payment_intent_id = charge.get('payment_intent')
            receipt_url = charge.get('receipt_url')

            if payment_intent_id and receipt_url:
                try:
                    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                    booking_id = payment_intent.metadata.get('booking_id')

                    if booking_id:
                        booking = Booking.objects.get(id=booking_id)
                        booking.receipt_url = receipt_url
                        booking.save()
                        booking.refresh_from_db()

                except Booking.DoesNotExist:
                    return HttpResponse(status=404)
                except Exception:
                    return HttpResponse(status=500)

        return HttpResponse(status=200)


def payment_success(request):
    return render(request, 'payments/success.html')

def payment_cancel(request):
    return render(request, 'payments/cancel.html')
