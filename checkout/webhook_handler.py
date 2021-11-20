from django.http import HttpResponse


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):  # The init method of the class is a setup method that's called every time an instance of the class is created.
        self.request = request  # we're going to use it to assign the request as an attribute of the class just in case we need to access any attributes of the request coming from stripe.

    def handle_event(self, event):  # create a class method called handle event which will take the event stripe is sending us and simply return an HTTP response indicating it was received.
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',  
            status=200)  # to designate that the generic handle event method here is receiving the webhook we are otherwise not handling change the content to unhandled webhook receive

    def handle_payment_intent_succeeded(self, event):  # This will be sent each time a user completes the payment process.
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        return HttpResponse( 
            content=f'Webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_payment_failed(self, event):  # In the event of their payment failing.
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
