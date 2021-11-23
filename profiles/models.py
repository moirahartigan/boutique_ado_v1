from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_countries.fields import CountryField


class UserProfile(models.Model):
    """
    A user profile model for maintaining default
    delivery information and order history
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # This is just like a foreign key except that it specifies that each user can only have one profile.
    # And each profile can only be attached to one user The rest of the fields in this model are the delivery information fields we want the
    # user to be able to provide defaults for.
    # These can come directly from the order model.
    default_phone_number = models.CharField(max_length=20, null=True, blank=True)  # add default to the beginning of each to be clear what they are for
    default_country = CountryField(blank_label='Country *', null=True, blank=True)
    default_postcode = models.CharField(max_length=20, null=True, blank=True)
    default_town_or_city = models.CharField(max_length=40, null=True, blank=True)
    default_street_address1 = models.CharField(max_length=80, null=True, blank=True)
    default_street_address2 = models.CharField(max_length=80, null=True, blank=True)
    default_county = models.CharField(max_length=80, null=True, blank=True)

    def __str__(self):
        return self.user.username   # returns the user name


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):  #  each time a user object is saved. We'll automatically either create a
# profile for them if the user has just been created.
# Or just save the profile to update it if the user already existed.
    """
    Create or update the user profile
    """
    if created:
        UserProfile.objects.create(user=instance)
    # Existing users: just save the profile
    instance.userprofile.save()

    # since there's only one signal I'm not putting it in a separate signals.py module
    # like we did for the ones on the order model.
