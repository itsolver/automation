#! /usr/bin/env python3.6

"""
server.py
Stripe Recipe.
Python 3.6 or newer required.
"""

import stripe
import json
import os

from flask import Flask, render_template, jsonify, request, send_from_directory
from dotenv import load_dotenv, find_dotenv

# Setup Stripe python client library
load_dotenv(find_dotenv())
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_version = os.getenv('STRIPE_API_VERSION')

static_dir = str(os.path.abspath(os.path.join(
    __file__, "..", os.getenv("STATIC_DIR"))))
app = Flask(__name__, static_folder=static_dir,
            static_url_path="", template_folder=static_dir)


@app.route('/', methods=['GET'])
def get_index():
    return render_template('index.html')


@app.route('/config', methods=['GET'])
def get_config():
    return jsonify(
        publishableKey=os.getenv('STRIPE_PUBLISHABLE_KEY'),
    )


@app.route('/create-customer', methods=['POST'])
def create_customer():
    # Reads application/json and returns a response
    data = json.loads(request.data)
    try:
        # Create a new customer object
        customer = stripe.Customer.create(
            email=data['email']
        )
        # At this point, associate the ID of the Customer object with your
        # own internal representation of a customer, if you have one.
        return jsonify(
            customer=customer,
        )
    except Exception as e:
        return jsonify(error=str(e)), 403


@app.route('/create-subscription', methods=['POST'])
def createSubscription():
    data = json.loads(request.data)
    try:

        stripe.PaymentMethod.attach(
            data['paymentMethodId'],
            customer=data['customerId'],
        )
        # Set the default payment method on the customer
        stripe.Customer.modify(
            data['customerId'],
            invoice_settings={
                'default_payment_method': data['paymentMethodId'],
            },
        )

        # Create the subscription
        subscription = stripe.Subscription.create(
            customer=data['customerId'],
            items=[
                {
                    'price': os.getenv(data['priceId'])
                }
            ],
            expand=['latest_invoice.payment_intent'],
        )
        return jsonify(subscription)
    except Exception as e:
        return jsonify(error={'message': str(e)}), 200


@app.route('/retry-invoice', methods=['POST'])
def retrySubscription():
    data = json.loads(request.data)
    try:

        stripe.PaymentMethod.attach(
            data['paymentMethodId'],
            customer=data['customerId'],
        )
        # Set the default payment method on the customer
        stripe.Customer.modify(
            data['customerId'],
            invoice_settings={
                'default_payment_method': data['paymentMethodId'],
            },
        )

        invoice = stripe.Invoice.retrieve(
            data['invoiceId'],
            expand=['payment_intent'],
        )
        return jsonify(invoice)
    except Exception as e:
        return jsonify(error={'message': str(e)}), 200


@app.route('/retrieve-upcoming-invoice', methods=['POST'])
def retrieveUpcomingInvoice():
    data = json.loads(request.data)
    try:
        # Retrieve the subscription
        subscription = stripe.Subscription.retrieve(data['subscriptionId'])

        # Retrive the Invoice
        invoice = stripe.Invoice.upcoming(
            customer=data['customerId'],
            subscription=data['subscriptionId'],
            subscription_items=[
                {
                    'id': subscription['items']['data'][0].id,
                    'deleted': True,
                    'clear_usage': True
                },
                {
                    'price': os.getenv(data['newPriceId']),
                    'deleted': False
                }
            ],
        )
        return jsonify(invoice)
    except Exception as e:
        return jsonify(error=str(e)), 403


@app.route('/cancel-subscription', methods=['POST'])
def cancelSubscription():
    data = json.loads(request.data)
    try:
        # Cancel the subscription by deleting it
        deletedSubscription = stripe.Subscription.delete(
            data['subscriptionId'])
        return jsonify(deletedSubscription)
    except Exception as e:
        return jsonify(error=str(e)), 403


@app.route('/update-subscription', methods=['POST'])
def updateSubscription():
    data = json.loads(request.data)
    try:
        subscription = stripe.Subscription.retrieve(data['subscriptionId'])

        updatedSubscription = stripe.Subscription.modify(
            data['subscriptionId'],
            cancel_at_period_end=False,
            items=[{
                'id': subscription['items']['data'][0].id,
                'price': os.getenv(data['newPriceId']),
            }]
        )
        return jsonify(updatedSubscription)
    except Exception as e:
        return jsonify(error=str(e)), 403


@app.route('/retrieve-customer-payment-method', methods=['POST'])
def retrieveCustomerPaymentMethod():
    data = json.loads(request.data)
    try:
        paymentMethod = stripe.PaymentMethod.retrieve(
            data['paymentMethodId'],
        )
        return jsonify(paymentMethod)
    except Exception as e:
        return jsonify(error=str(e)), 403


@app.route('/stripe-webhook', methods=['POST'])
def webhook_received():

    # You can use webhooks to receive information about asynchronous payment events.
    # For more about our webhook events check out https://stripe.com/docs/webhooks.
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    request_data = json.loads(request.data)

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']

        data_object = data['object']

    if event_type == 'invoice.paid':
        # Used to provision services after the trial has ended.
        # The status of the invoice will show up as paid. Store the status in your
        # database to reference when a user accesses your service to avoid hitting rate
        # limits.
        # print(data)
        print(invoice.paid)
    if event_type == 'invoice.payment_failed':
        # If the payment fails or the customer does not have a valid payment method,
        # an invoice.payment_failed event is sent, the subscription becomes past_due.
        # Use this webhook to notify your user that their payment has
        # failed and to retrieve new card details.
        # print(data)
        print(invoice.payment_failed)

    if event_type == 'invoice.finalized':
        # If you want to manually send out invoices to your customers
        # or store them locally to reference to avoid hitting Stripe rate limits.
        process_lines(data)

    if event_type == 'customer.subscription.deleted':
        # handle subscription cancelled automatically based
        # upon your subscription settings. Or if the user cancels it.
        # print(data)
        print(customer.subscription.deleted)

    if event_type == 'customer.subscription.trial_will_end':
        # Send notification to your user that the trial will end
        # print(data)
        print(customer.subscription.trial_will_end)

    return jsonify({'status': 'success'})


def process_lines(data):
    quantity_corrected = []
    amount_decimal = []
    descriptions = []
    quantities = []
    amounts = []

    for j, line in enumerate(data['object']['lines']['data']):
        proration = line['proration']
        tiers_mode = line['plan']['tiers_mode']
        nickname = line['plan']['nickname']
        description = line['description']
        quantity = line['quantity']
        amount = None

        if tiers_mode == 'graduated':
            for tier in line['plan']['tiers']:
                tiers_flat_amount = tier['flat_amount']
                tiers_up_to = tier['up_to']
                tiers_unit_amount = tier['unit_amount']
                tiers_flat_up_to = line['plan']['tiers'][0]['up_to']
                # Tier 1 usage
                if quantity == 0:
                    print('Skipping invoice line with 0 quantity')
                elif "Tier 1" in description and (tiers_flat_amount != None) and (tiers_up_to != None) and (quantity > 0):
                    description = description + '. Flat fee for first ' + \
                        str(tiers_up_to) + ' users'
                    quantity_flat_rate = 1
                    amount = tiers_flat_amount/100
                    descriptions.append(description)
                    quantities.append(quantity_flat_rate)
                    amounts.append(amount)
                # Tier 2 usage
                elif "Tier 2" in description and (tiers_flat_amount == None) and (tiers_up_to == None) and (quantity > 0):
                    description = str(line['plan']['tiers']
                                      [0]['up_to']+1) + ' and above'
                    quantity_tier_2 = line['quantity']
                    amount = tiers_unit_amount/100
                    descriptions.append(description)
                    quantities.append(quantity_tier_2)
                    amounts.append(amount)
                elif proration and quantity > 0 and tiers_flat_amount != None:
                    description = str(description)
                    quantity = 1
                    amount = line['amount']/100
                    descriptions.append(description)
                    quantities.append(quantity)
                    amounts.append(amount)

        # Non-tiered plans
        elif not proration:
            description = line['plan']['nickname']
            amount = line['plan']['amount']/100
            descriptions.append(description)
            quantities.append(quantity)
            amounts.append(amount)
        elif proration:
            description = line['description']
            amount = line['amount']/100
            quantity = 1
            descriptions.append(description)
            quantities.append(quantity)
            amounts.append(amount)

    output = [{'descriptions': descriptions,
               'quantities': quantities, 'amount_decimal': amounts}]
    print(output)


if __name__ == '__main__':
    app.run(port=4242)
