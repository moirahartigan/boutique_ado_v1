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
card.addEventListener('change', function (event) { // add a listener on card element for the change event. every time it changes we'll check to see if there are any errors
    var errorDiv = document.getElementById('card-errors');
    if (event.error) { // If so we'll display them in the card errors div we created near the card element on the checkout page.
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
    stripe.confirmCardPayment(clientSecret, {  // It uses the stripe.confirm card payment method to send the card information securely to stripe.
        payment_method: {
            card: card,
        }
    }).then(function(result) { // then execute this function on the result
        if (result.error) {
            var errorDiv = document.getElementById('card-errors'); // if there is an error we get an error message
            var html = `
                <span class="icon" role="alert">
                <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`;
            $(errorDiv).html(html); // if there is an error the user is allowed to fix it
            card.update({ 'disabled': false});
            $('#submit-button').attr('disabled', false);
        } else {
            if (result.paymentIntent.status === 'succeeded') { // if status come back as succeeded we submit the form
                form.submit();
            }
        }
    });
});