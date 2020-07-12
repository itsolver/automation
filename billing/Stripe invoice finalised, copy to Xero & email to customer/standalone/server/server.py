#! /usr/bin/env python3.6

"""
server.py
Stripe Recipe.
Python 3.6 or newer required.
"""

import datetime
from decimal import Decimal
from xero_python.utils import getvalue
from xero_python.identity import IdentityApi
from xero_python.exceptions import AccountingBadRequestException
from xero_python.api_client.oauth2 import OAuth2Token
from xero_python.api_client.configuration import Configuration
from xero_python.api_client import ApiClient, serialize
from xero_python.accounting import AccountingApi, ContactPerson, Contact, Contacts, Invoice, Invoices, LineItem
from flask_session import Session
from flask_oauthlib.contrib.client import OAuth, OAuth2Application
from flask import Flask, url_for, render_template, session, redirect, json, send_file
from logging.config import dictConfig
from io import BytesIO
from functools import wraps
import stripe
import json
import os
from utils import jsonify, serialize_model


import time
import xero_python
from xero_python.exceptions import ApiException
from pprint import pprint

from flask import Flask, render_template, jsonify, request, send_from_directory
from dotenv import load_dotenv, find_dotenv

# Setup Stripe python client library
load_dotenv(find_dotenv())
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_version = os.getenv('STRIPE_API_VERSION')

# Xero-Python-OAuth2

# import logging_settings

# dictConfig(logging_settings.default_settings)

# configure main flask application
app = Flask(__name__)
app.config.from_object("default_settings")
env = os.getenv('ENV')

if env != "production":
    # allow oauth2 loop to run over http (used for local testing only)
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# configure persistent session cache
Session(app)

# configure flask-oauthlib application
# TODO fetch config from https://identity.xero.com/.well-known/openid-configuration #1
oauth = OAuth(app)
xero = oauth.remote_app(
    name="xero",
    version="2",
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    endpoint_url="https://api.xero.com/",
    authorization_url="https://login.xero.com/identity/connect/authorize",
    access_token_url="https://identity.xero.com/connect/token",
    refresh_token_url="https://identity.xero.com/connect/token",
    scope="offline_access openid profile email accounting.transactions "
    "accounting.transactions.read accounting.reports.read "
    "accounting.journals.read accounting.settings accounting.settings.read "
    "accounting.contacts accounting.contacts.read accounting.attachments "
    "accounting.attachments.read assets projects",
)  # type: OAuth2Application


# configure xero-python sdk client
api_client = ApiClient(
    Configuration(
        debug=app.config["DEBUG"],
        oauth2_token=OAuth2Token(
            client_id=os.getenv("CLIENT_ID"), client_secret=os.getenv("CLIENT_SECRET")
        ),
    ),
    pool_threads=1,
)


# configure token persistence and exchange point between flask-oauthlib and xero-python
@xero.tokengetter
@api_client.oauth2_token_getter
def obtain_xero_oauth2_token():
    return session.get("token")


@xero.tokensaver
@api_client.oauth2_token_saver
def store_xero_oauth2_token(token):
    session["token"] = token
    session.modified = True


def xero_token_required(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        xero_token = obtain_xero_oauth2_token()
        if not xero_token:
            return redirect(url_for("login", _external=True))

        return function(*args, **kwargs)

    return decorator


@app.route("/login")
def login():
    redirect_url = url_for("oauth_callback", _external=True)
    response = xero.authorize(callback_uri=redirect_url)
    return response


@app.route("/callback")
def oauth_callback():
    try:
        response = xero.authorized_response()
    except Exception as e:
        print(e)
        raise
    # todo validate state value
    if response is None or response.get("access_token") is None:
        return "Access denied: response=%s" % response
    store_xero_oauth2_token(response)
    return redirect(url_for("index", _external=True))


@app.route("/logout")
def logout():
    store_xero_oauth2_token(None)
    return redirect(url_for("index", _external=True))


@app.route("/export-token")
@xero_token_required
def export_token():
    token = obtain_xero_oauth2_token()
    buffer = BytesIO("token={!r}".format(token).encode("utf-8"))
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="x.python",
        as_attachment=True,
        attachment_filename="oauth2_token.py",
    )


@app.route("/refresh-token")
@xero_token_required
def refresh_token():
    xero_token = obtain_xero_oauth2_token()
    new_token = api_client.refresh_oauth2_token()
    return render_template(
        "code.html",
        title="Xero OAuth2 token",
        code=jsonify({"Old Token": xero_token, "New token": new_token}),
        sub_title="token refreshed",
    )


def get_xero_tenant_id():
    token = obtain_xero_oauth2_token()
    if not token:
        return None

    identity_api = IdentityApi(api_client)
    for connection in identity_api.get_connections():
        if connection.tenant_type == "ORGANISATION":
            return connection.tenant_id


@app.route("/tenants")
@xero_token_required
def tenants():
    identity_api = IdentityApi(api_client)
    accounting_api = AccountingApi(api_client)

    available_tenants = []
    for connection in identity_api.get_connections():
        tenant = serialize(connection)
        if connection.tenant_type == "ORGANISATION":
            organisations = accounting_api.get_organisations(
                xero_tenant_id=connection.tenant_id
            )
            # tenant["organisations"] = serialize(organisations)

        available_tenants.append(tenant)

    return render_template(
        "code.html",
        title="Xero Tenants",
        code=json.dumps(available_tenants, sort_keys=True, indent=4),
    )


@app.route("/create_invoices")
def create_invoices():
    xero_tenant_id = get_xero_tenant_id()
    accounting_api = AccountingApi(api_client)

    contact = Contact(
        contact_id="571a2414-81ff-4f8f-8498-d91d83793131")
    line_items = LineItem(
        account_code="200",
        description="Acme Tires",
        line_amount=Decimal("40.00"),
        line_item_id="5f7a612b-fdcc-4d33-90fa-a9f6bc6db32f",
        quantity=Decimal("2.0000"),
        tax_amount=Decimal("0.00"),
        tax_type="NONE",
        unit_amount=Decimal("20.00")
    )

    invoices = Invoice(type="ACCREC", due_date=datetime.date(2020, 7, 13),
                       status="AUTHORISED", contact=contact, line_items=[line_items])

    try:
        created_invoices = accounting_api.create_invoices(
            xero_tenant_id, invoices)
        print(created_invoices)
    except AccountingBadRequestException as exception:
        sub_title = "Error: " + exception.reason
        code = jsonify(exception.error_data)
    else:
        sub_title = "Invoice {} created.".format(
            getvalue(created_invoices, "invoice.0.number", "")
        )
        code = serialize_model(created_invoices)

    return render_template(
        "code.html", title="Create Invoices", code=code, sub_title=sub_title
    )


@app.route("/")
def index():
    xero_access = dict(obtain_xero_oauth2_token() or {})
    return render_template(
        "code.html",
        title="Home | oauth token",
        code=json.dumps(xero_access, sort_keys=True, indent=4),
    )


@app.route('/config', methods=['GET'])
def get_config():
    return jsonify(
        publishableKey=os.getenv('STRIPE_PUBLISHABLE_KEY'),
    )


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
    app.run(host="localhost")
    app.run(port=5000)
