from django.http import HttpResponse

from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile

import json
import time


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
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount / 100, 2)

        # Clean data in the shipping details
        for field, value in shipping_details.address.items():  # to ensure the data is in the same form as what we want in our database. 
            # replace any empty strings in the shipping details with none
            if value == "":
                shipping_details.address[field] = None

        # Update profile information if save_info was checked
        profile = None  # profile set to none. Just so we know we can still allow anonymous users to checkout.
        username = intent.metadata.username  # get the username
        if username != 'AnonymousUser':
            profile = UserProfile.objects.get(user__username=username)  # if not anonymous let's try to get their profile using their username
            if save_info:  # If they've got the save info box checked which comes from the metadata. Then we want to update their profile by adding the shipping details as their default delivery information
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_postcode = shipping_details.address.postal_code
                profile.default_town_or_city = shipping_details.address.city
                profile.default_street_address1 = shipping_details.address.line1
                profile.default_street_address2 = shipping_details.address.line2
                profile.default_county = shipping_details.address.state
                profile.save()

        order_exists = False  # assum the order doesnt exist
        attempt = 1
        while attempt <= 5:
            try:  # try to get the order using all the information from the payment intent. And I'm using the iexact lookup field to make it an exact match but case-insensitive
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                break  # if the order is found break out of the loop
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:  # if the order is found we'll set order exists to true and return a 200 HTTP response to stripe, with the message that we verified the order already exists.
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200)
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    # since we've already got their profile and if they weren't logged in it will just be none.
                    # We can simply add it to their order when the webhook creates it.
                    # In this way, the webhook handler can create orders for both authenticated users by attaching their profile.
                    # And for anonymous users by setting that field to none.
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        return HttpResponse(  # if anything goes wrong I'll just delete the order if it was created. And return a 500 server error response to stripe. This will cause stripe to automatically try the webhook again later
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)

    def handle_payment_intent_payment_failed(self, event):  # In the event of their payment failing.
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
