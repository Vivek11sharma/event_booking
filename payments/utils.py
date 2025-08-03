import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_checkout_session(booking):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(booking.total_amount * 100),
                    'product_data': {
                        'name': f'Tickets for {booking.event.title}',
                    },
                },
                'quantity': 1,
            },
        ],
        mode='payment',
        success_url='http://localhost:8000/payment/success/',
        cancel_url='http://localhost:8000/payment/cancel/',
        payment_intent_data={   
            'metadata': {
                'booking_id': str(booking.id),
            }
        },
        expand=['payment_intent.charges']

    )
    return session.url