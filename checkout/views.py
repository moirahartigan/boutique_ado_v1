from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm


def checkout(request):
    bag = request.session.get('bag', {}) # get the bag from the session
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products')) # redirect back to the products page

    order_form = OrderForm() # create an instance of our order form. Which will be empty for now.
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form, # context containing the order form
    }

    return render(request, template, context)
