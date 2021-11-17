from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order # tell django which model to use
        fields = ('full_name', 'email', 'phone_number',
                  'street_address1', 'street_address2',
                  'town_or_city', 'postcode', 'country',
                  'county',)

    def __init__(self, *args, **kwargs): # override init to allow us to customize it
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs) # first call default init to set the form up
        placeholders = { # create dictionary of placeholders which will show up in the form fields rather than having clunky looking labels and empty text boxes in the template
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'country': 'Country',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County',
        }

        self.fields['full_name'].widget.attrs['autofocus'] = True # set the autofocus attribute on the full name field to true so the cursor will start in the full name field when the user loads the page.
        for field in self.fields: #  iterate through the forms fields
            if self.fields[field].required:
                placeholder = f'{placeholders[field]} *' # adding a star to the placeholder if it's a required field on the model.
            else:
                placeholder = placeholders[field]
            self.fields[field].widget.attrs['placeholder'] = placeholder # and Setting all the placeholder attributes to their values in the dictionary above
            self.fields[field].widget.attrs['class'] = 'stripe-style-input' # adding a css class to use later
            self.fields[field].label = False # then removing the form fields labels. Since we won't need them given the placeholders are now set.