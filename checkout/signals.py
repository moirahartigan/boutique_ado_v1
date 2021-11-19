# Post, in this case, means after. So this implies these signals are sent by django to the entire application
# after a model instance is saved and after it's deleted respectively.
from django.db.models.signals import post_save, post_delete
# To receive these signals we can import receiver from django.dispatch.
from django.dispatch import receiver
# since we'll be listening for signals from the OrderLineItem model we'll also need that
from .models import OrderLineItem

@receiver(post_save, sender=OrderLineItem) # to execute this function anytime the post_save signal is sent
# This is a special type of function which will handle signals from the post_save event.
# So these parameters refer to the sender of the signal. In our case OrderLineItem.
# The actual instance of the model that sent it.
def update_on_save(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    instance.order.update_total() # we just have to access instance.order which refers to the order this specific line item is related to. And call the update_total method on it.

@receiver(post_delete, sender=OrderLineItem) # to execute this function anytime the post_save signal is sent
def update_on_delete(sender, instance, **kwargs):
    """
    Update order total on lineitem delete
    """
    instance.order.update_total()