import uuid  # used to generate the order no

from django.db import models
from django.db.models import Sum
from django.conf import settings

from products.models import Product


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = models.CharField(max_length=40, null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)

    # order method _means private method that will only be used inside this class
    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper() # will just generate a random string of 32 characters we can use as an order number

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        # The way this works is by using the sum function across all the line-item total fields for all line items on this order.
        # The default behaviour is to add a new field to the query set called line-item total sum.
        # Which we can then get and set the order total to that.
        self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum'] or 0
        # we can then calculate the delivery cost
        # using the free delivery threshold and the standard delivery percentage from our settings file.
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
        else:
            # Setting it to zero if the order total is higher than the threshold.
            self.delivery_cost = 0
            # then to calculate the grand total
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    # override the default save method
    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    # standard string method, returning just the order number for the order model.
    def __str__(self):
        return self.order_number

    # A line-item will be like an individual shopping bag item. Relating to a specific order
    # And referencing the product itself. The size that was selected. The quantity.
    # And the total cost for that line item.
    # A line-item will be like an individual shopping bag item. Relating to a specific order
    # And referencing the product itself. The size that was selected. The quantity.
    # And the total cost for that line item.
class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems')
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE)
    product_size = models.CharField(max_length=2, null=True, blank=True) # XS, S, M, L, XL
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)

    # need to set the line-item total field on the order line-item model by overriding its save method.
    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        # just need to multiply the product price by the quantity for each line item
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

# standard string method, returning just the order number for the order model.
# And the SKU of the product along with the order number it's part of for each order line item
    def __str__(self):
        return f'SKU {self.product.sku} on order {self.order.order_number}'
