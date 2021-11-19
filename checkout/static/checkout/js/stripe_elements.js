/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment
    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

// get the stripe public key.
var stripe_public_key = $('#id_stripe_public_key').text().slice(1, -1);
// And client secret from the template using a little jQuery slice off the first and last character on each since they'll have quotation marks which we don't want
var client_secret = $('#id_client_secret').text().slice(1, -1);
// made possible by the stripe js included in the base template. All we need to do to set up stripe is create a variable using our stripe public key
var stripe = Stripe(stripe_public_key);
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