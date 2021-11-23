from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from .models import UserProfile
from .forms import UserProfileForm


def profile(request):
    """ Display the user's profile. """
    profile = get_object_or_404(UserProfile, user=request.user)

    # if the request method is post.
    # Create a new instance of the user profile form using the post data.
    # And tell it the instance we're updating is the profile we've just retrieved above.
    # Then if the form is valid. We'll simply save it and add a success message.
    # And that means we'll also need to import messages
    if request.method == 'POST':  # post handler 
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')

    form = UserProfileForm(instance=profile)
    orders = profile.orders.all()

    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True
    }

    return render(request, template, context)