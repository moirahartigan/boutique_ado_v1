from django import forms
from .models import UserProfile  # change the import


class UserProfileForm(forms.ModelForm):  # change the class name
    class Meta:
        model = UserProfile  # change this to UserProfile
        exclude = ('user',)  # rather than having a fields attribute we set the exclude attribute and render all fields except for the user field since that should never change

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)
        placeholders = {  # get rid of full name and email as they dont exist on this model and add default in front of the fiels names
            'default_phone_number': 'Phone Number',
            'default_postcode': 'Postal Code',
            'default_town_or_city': 'Town or City',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
            'default_county': 'County, State or Locality',
        }

        self.fields['default_phone_number'].widget.attrs['autofocus'] = True  # change the autofocus to default phone number
        for field in self.fields:
            if field != 'default_country':
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'border-black rounded-0 profile-form-input'  # change the classes we're adding. To make the form match the rest of our theme
            self.fields[field].label = False