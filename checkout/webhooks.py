from django.conf import settings  # to get the webhook and the stripe API secrets
from django.http import HttpResponse  # so these exception handlers will work
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from checkout.webhook_handler import StripeWH_Handler  # webhook handler class and stripe

import stripe

@require_POST  # will make this view require a post request and will reject get requests
@csrf_exempt  # since stripe won't send a CSRF token like we'd normally need.
#-------------------- this code is taken directly from stripe -------------------------
def webhook(request):
    """Listen for webhooks from Stripe"""
    # Setup
    wh_secret = settings.STRIPE_WH_SECRET  # change the name of endpoint_secret to wh_secret which we'll create in a moment
    stripe.api_key = settings.STRIPE_SECRET_KEY  

    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']  # webhook secret which will be used to verify that the webhook actually came from stripe
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, wh_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:  # add a generic exception handler to catch any exceptions other than the two stripe has provided
        # Invalid signature
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(content=e, status=400)

# -------------------------------- from here is code we have replaced with our own ---------------------
    # Set up a webhook handler
    handler = StripeWH_Handler(request)  # create an instance of it passing in the request

    # Map webhook events to relevant handler functions
    event_map = {  # dictionary called event_map with keys webhooks coming from stripe and values are the actual methods inside the handler
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed,
    }

    # Get the webhook type from Stripe
    event_type = event['type']

    # If there's a handler for it, get it from the event map
    # Use the generic one by default
    event_handler = event_map.get(event_type, handler.handle_event)

    # Call the event handler with the event
    response = event_handler(event)
    return response
    