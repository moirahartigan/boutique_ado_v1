from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from bag.contexts import bag_contents

import stripe
import json

@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':  # check whether the method is post.That means we should also wrap the current code into an else block to handle the get requests. In the post method code we will need the shopping bag.
        bag = request.session.get('bag', {})

        form_data = {  # form data will be in a dictionary
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        order_form = OrderForm(form_data)  # create an instance of the form using the form data from line 17
        if order_form.is_valid():  # if the form is valid we will save the order
            order = order_form.save(commit=False)  # prevent multiple save events from being executed on the database By adding commit equals false here to prevent the first one from happening
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            order.save()
            for item_id, item_data in bag.items():  # then itterate throught the bag items to create each line item
                try:
                    product = Product.objects.get(id=item_id)  # first we get the product id out of the bag
                    if isinstance(item_data, int):  # if no sizes then its just item data
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:  # otherwise we iterate through each size and create a line item accordingly 
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                except Product.DoesNotExist:  # just incase a product isnt found we add an error message
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    order.delete()  # delete the empty order
                    return redirect(reverse('view_bag'))  # and return the user to the shopping bag page

            request.session['save_info'] = 'save-info' in request.POST  # We'll attach whether or not the user wanted to save their profile information to the session.
            return redirect(reverse('checkout_success', args=[order.order_number]))  # And then redirect them to a new page checkout success and pass it the order number
        else:
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')  # if the order form isnt valid they will be sent back to the checkout pg
    else:
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

        order_form = OrderForm() # create an instance of our order form. Which will be empty for now.

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form, # context containing the order form
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    save_info = request.session.get('save_info')  # first check whether the user wanted to save their info by getting that from the session 
    order = get_object_or_404(Order, order_number=order_number)  # use the order number to get the order created in the previous view which we'll send back to the template.
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')  # attach a success message letting the user know what their order number is.

    if 'bag' in request.session:
        del request.session['bag']  # delete the user shopping bag from the session

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,  # Set the template and the context. And render the template.
    }

    return render(request, template, context)
