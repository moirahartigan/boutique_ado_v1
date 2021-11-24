/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment
    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

// get the stripe public key.
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
// And client secret from the template using a little jQuery slice off the first and last character on each since they'll have quotation marks which we don't want
var clientSecret = $('#id_client_secret').text().slice(1, -1);
// made possible by the stripe js included in the base template. All we need to do to set up stripe is create a variable using our stripe public key
var stripe = Stripe(stripePublicKey);
// we can use it to create an instance of stripe elements
var elements = stripe.elements();
// The card element can also accept a style argument. So get some basic styles direct from the stripe js Docs. (copy)
var style = {
    base: {
        color: '#000', // update is the default colour of the element to black
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545' // change the invalid colour to match bootstraps text danger class
    }
};
// create a card element
var card = elements.create('card', {style: style});
// and mount the card element to the div we created 
card.mount('#card-element');

// Handle realtime validation errors on the card element
card.addEventListener('change', function (event) {   // add a listener on card element for the change event. every time it changes we'll check to see if there are any errors
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {   // If so we'll display them in the card errors div we created near the card element on the checkout page.
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submit
var form = document.getElementById('payment-form'); // After getting the form element the first thing the listener does is prevent its default action which in our case is to post.

form.addEventListener('submit', function(ev) {
    ev.preventDefault();
    card.update({ 'disabled': true});  // before we call out to stripe. We'll want to disable both the card element and the submit button to prevent multiple submissions
    $('#submit-button').attr('disabled', true);
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);

    var saveInfo = Boolean($('#id-save-info').attr('checked'));
    // From using {% csrf_token %} in the form
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    var postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    };
    var url = '/checkout/cache_checkout_data/';

    $.post(url, postData).done(function () {
        stripe.confirmCardPayment(clientSecret, {   // It uses the stripe.confirm card payment method to send the card information securely to stripe.
            payment_method: {
                card: card,
                billing_details: {
                    name: $.trim(form.full_name.value),
                    phone: $.trim(form.phone_number.value),
                    email: $.trim(form.email.value),
                    address:{
                        line1: $.trim(form.street_address1.value),
                        line2: $.trim(form.street_address2.value),
                        city: $.trim(form.town_or_city.value),
                        country: $.trim(form.country.value),
                        state: $.trim(form.county.value),
                    }
                }
            },
            shipping: {
                name: $.trim(form.full_name.value),
                phone: $.trim(form.phone_number.value),
                address: {
                    line1: $.trim(form.street_address1.value),
                    line2: $.trim(form.street_address2.value),
                    city: $.trim(form.town_or_city.value),
                    country: $.trim(form.country.value),
                    postal_code: $.trim(form.postcode.value),
                    state: $.trim(form.county.value),
                }
            },
        }).then(function(result) {   // then execute this function on the result
            if (result.error) {
                var errorDiv = document.getElementById('card-errors');  // if there is an error we get an error message
                var html = `
                    <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                    </span>
                    <span>${result.error.message}</span>`;
                $(errorDiv).html(html); // if there is an error the user is allowed to fix it
                $('#payment-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                card.update({ 'disabled': false});
                $('#submit-button').attr('disabled', false);
            } else {
                if (result.paymentIntent.status === 'succeeded') {   // if status come back as succeeded we submit the form
                    form.submit();
                }
            }
        });
    }).fail(function () {  // failure function, which will be triggered if our view sends a 400 bad request response. And in that case, we'll just reload the page to show the user the error message from the view just reload the page, the error will be in django messages
        location.reload();
    })
});

// Summary of what happens
// When the user clicks the submit button the event listener prevents the form from submitting
// and instead disables the card element and triggers the loading overlay.
// Then we create a few variables to capture the form data we can't put in
// the payment intent here, and instead post it to the cache_checkout_data view
// The view updates the payment intent and returns a 200 response, at which point we
// call the confirm card payment method from stripe and if everything is ok
// submit the form.
// If there's an error in the form then the loading overlay will
// be hidden the card element re-enabled and the error displayed for the user.
// If anything goes wrong posting the data to our view. We'll reload the page and
// display the error without ever charging the user.
// https://learn.codeinstitute.net/courses/course-v1:CodeInstitute+EA101+2021_T1/courseware/eb05f06e62c64ac89823cc956fcd8191/48ac02aa8ecc4079be016c336231bee7/