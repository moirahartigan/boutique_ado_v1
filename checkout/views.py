from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from bag.contexts import bag_contents

import stripe

def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    bag = request.session.get('bag', {})  # get the bag from the session
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))  # redirect back to the products page

    # for stripe
    current_bag = bag_contents(request)  # for stripe store variable called current bag
    total = current_bag['grand_total']  # to get the total all I need to do is get the grand_total key out of the current bag.
    stripe_total = round(total * 100)  # I'll multiply that by a hundred and round it to zero decimal places using the round function
    stripe.api_key = stripe_secret_key  # set the secret key on stripe
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    order_form = OrderForm() # create an instance of our order form. Which will be empty for now.
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form, # context containing the order form
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)
