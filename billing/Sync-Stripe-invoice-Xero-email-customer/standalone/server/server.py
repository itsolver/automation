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
from xero_python.accounting import (
    AccountingApi, ContactPerson, Contact, Contacts, Invoice, Invoices, LineItem, LineAmountTypes,)
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
from gmail import create_message_with_attachment, send_message, gmail_creds
from pathlib import Path
import json


import time
import xero_python
from xero_python.exceptions import ApiException
from pprint import pprint

from flask import Flask, render_template, jsonify, request, send_from_directory
from dotenv import load_dotenv, find_dotenv

import locale
from pathlib import Path

currency = 'en_AU.UTF-8'
locale.setlocale(locale.LC_ALL, currency)
conv = locale.localeconv()

# Store secrets outside of this repository
xero_oauth_token_path = 'C:/Users/Test/secrets/itsolver/automation/billing/oauth2_token'
env_path = Path(r'C:\Users\Test\secrets\itsolver\automation\billing') / '.env'
load_dotenv(dotenv_path=env_path)


# Setup Stripe python client library

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_version = os.getenv('STRIPE_API_VERSION')

# Xero settings
branding_theme_id = os.getenv('BRANDING_THEME_ID')

# Email settings
sender_name = os.getenv('SENDER_NAME')
sender_email = os.getenv('SENDER_EMAIL')

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
    app.debug = True


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
        oauth2_token=OAuth2Token(
            client_id=os.getenv("CLIENT_ID"), client_secret=os.getenv("CLIENT_SECRET")
        ),
    ),
    pool_threads=1,
)


# configure token persistence and exchange point between flask-oauthlib and xero-python
@ xero.tokengetter
@ api_client.oauth2_token_getter
def obtain_xero_oauth2_token():
    with open(xero_oauth_token_path) as json_file:
        token = json.load(json_file)
        return token


@ xero.tokensaver
@ api_client.oauth2_token_saver
def store_xero_oauth2_token(token):
    with open(xero_oauth_token_path, 'w') as outfile:
        json.dump(token, outfile)


def xero_token_required(function):
    @ wraps(function)
    def decorator(*args, **kwargs):
        xero_token = obtain_xero_oauth2_token()
        if not xero_token:
            return redirect(url_for("login", _external=True))

        return function(*args, **kwargs)

    return decorator


@ app.route("/login")
def login():
    redirect_url = url_for("oauth_callback", _external=True)
    response = xero.authorize(callback_uri=redirect_url)
    return response


@ app.route("/callback")
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


@ app.route("/logout")
def logout():
    store_xero_oauth2_token(None)
    return redirect(url_for("index", _external=True))


@ app.route("/export-token")
@ xero_token_required
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


@ app.route("/refresh-token")
@ xero_token_required
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
    xero_tenant_id = os.getenv('XERO_TENANT_ID')
    token = obtain_xero_oauth2_token()
    if not token:
        return None

    identity_api = IdentityApi(api_client)
    for connection in identity_api.get_connections():
        if connection.tenant_id == xero_tenant_id:
            return connection.tenant_id


@ app.route("/tenants")
@ xero_token_required
def tenants():
    identity_api = IdentityApi(api_client)

    available_tenants = []
    for connection in identity_api.get_connections():
        tenant = serialize(connection)
        available_tenants.append(tenant)

    return render_template(
        "code.html",
        title="Xero Tenants",
        code=json.dumps(available_tenants, sort_keys=True, indent=4),
    )


@ app.route("/")
def index():
    xero_access = dict(obtain_xero_oauth2_token() or {})
    return render_template(
        "code.html",
        title="Home | oauth token",
        code=json.dumps(xero_access, sort_keys=True, indent=4),
    )


@ app.route('/config', methods=['GET'])
def get_config():
    return jsonify(
        publishableKey=os.getenv('STRIPE_PUBLISHABLE_KEY'),
    )


@ app.route('/stripe-webhook', methods=['POST'])
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

    if event_type == 'invoice.paid':
        # Used to provision services after the trial has ended.
        # The status of the invoice will show up as paid. Store the status in your
        # database to reference when a user accesses your service to avoid hitting rate
        # limits.
        # print(data)
        print("invoice.paid")
    if event_type == 'invoice.payment_failed':
        # If the payment fails or the customer does not have a valid payment method,
        # an invoice.payment_failed event is sent, the subscription becomes past_due.
        # Use this webhook to notify your user that their payment has
        # failed and to retrieve new card details.
        # print(data)
        print("invoice.payment_failed")

    if event_type == 'invoice.finalized':
        # If you want to manually send out invoices to your customers
        # or store them locally to reference to avoid hitting Stripe rate limits.
        process_lines(data)

    if event_type == 'customer.subscription.deleted':
        # handle subscription cancelled automatically based
        # upon your subscription settings. Or if the user cancels it.
        # print(data)
        print("customer.subscription.deleted")

    if event_type == 'customer.subscription.trial_will_end':
        # Send notification to your user that the trial will end
        # print(data)
        print("customer.subscription.trial_will_end")

    return jsonify({'status': 'success'})


def process_lines(data):
    descriptions = []
    quantities = []
    amounts = []
    sales_accounts = []

    for j, line in enumerate(data['object']['lines']['data']):
        sales_account = getvalue(
            line, 'plan.metadata.sales_account', '203')  # TODO: check tiered pricing isn't always defaulting because incorrect path to sales_account metadata
        sales_accounts.append(sales_account)
        proration = line['proration']
        tiers_mode = line['plan']['tiers_mode']
        description = line['description']
        quantity = line['quantity']
        amount = None

        if tiers_mode == 'graduated':
            for tier in line['plan']['tiers']:
                tiers_flat_amount = tier['flat_amount']
                tiers_up_to = tier['up_to']
                tiers_unit_amount = tier['unit_amount']
                # Tier 1 usage
                if quantity == 0:
                    print('Skipping invoice line with 0 quantity')
                elif "Tier 1" in description and (tiers_flat_amount != None) and (tiers_up_to != None) and (quantity > 0):
                    # description = description + '. Flat fee for first ' + \
                    #     str(tiers_up_to) + ' users'
                    next = j+1
                    description = data['object']['lines']['data'][next]['description']
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

    invoice_number = data['object']['number']
    name = data['object']['customer_name']
    email_address = data['object']['customer_email']
    status = data['object']['status']
    total = Decimal(data['object']['total'])/100
    total = str(round(total, 2))

    line_data = [{'descriptions': descriptions,
                  'quantities': quantities, 'amount_decimal': amounts}]
    created = data['object']['created']
    year_due = int(datetime.datetime.utcfromtimestamp(created).strftime('%Y'))
    month_due = int(datetime.datetime.utcfromtimestamp(created).strftime('%m'))
    day_due = int(datetime.datetime.utcfromtimestamp(created).strftime('%d'))
    print('-----------------------------------')
    print(name)
    print(email_address)
    print('{s}{a}'.format(s=conv['currency_symbol'], a=total))
    line_items = []
    for j, line in enumerate(line_data[0]['descriptions']):
        quantity = line_data[0]['quantities'][j]
        amount = line_data[0]['amount_decimal'][j]
        line_items.append(LineItem(account_code=sales_account, description=line, unit_amount=Decimal(
            amount), quantity=Decimal(quantity), tax_type="OUTPUT"))
    create_invoices(invoice_number, year_due, month_due,
                    day_due, name, email_address, line_items, status, total, branding_theme_id)


@ app.route("/create_invoices")
def create_invoices(invoice_number, year_due, month_due, day_due, name, email_address, line_items, status, total, branding_theme_id):
    xero_tenant_id = get_xero_tenant_id()
    accounting_api = AccountingApi(api_client)

    contact = Contact(
        name=name,
        email_address=email_address)

    invoices = Invoice(type="ACCREC", date=datetime.date(year_due, month_due, day_due), due_date=datetime.date(year_due, month_due, day_due),
                       status="AUTHORISED", invoice_number=invoice_number, contact=contact, line_items=line_items, line_amount_types=LineAmountTypes.INCLUSIVE, sent_to_contact=True, branding_theme_id=branding_theme_id)

    try:
        created_invoices = accounting_api.create_invoices(
            xero_tenant_id, invoices)
    except AccountingBadRequestException as exception:
        sub_title = "Error: " + exception.reason
        #code = exception.error_data
        print(sub_title)
        # print(code)
        # TODO log error and send me an email notification
    else:
        sub_title = "Invoice {} created".format(
            getvalue(created_invoices, "invoices.0.invoice_number", "")
        )
        print(sub_title)
        contact_number = created_invoices._invoices[0]._contact.contact_id
        invoice_id = created_invoices._invoices[0].invoice_id
        #invoice_url = get_online_invoice(xero_tenant_id, invoice_id)
        fname_default = os.getenv('FNAME_DEFAULT')
        provider_company_name = os.getenv('PROVIDER_COMPANY_NAME')
        gmail_api_username = os.getenv('GMAIL_API_USERNAME')
        fname = created_invoices._invoices[0].contact.first_name
        if fname == '':
            fname = fname_default
        invoice_number = created_invoices._invoices[0].invoice_number
        subject = "Your {} Invoice {}".format(
            provider_company_name, invoice_number)
        total_str = '{s}{a}'.format(s=conv['currency_symbol'], a=total)
        if status == 'paid':
            # ISSUE: Payment successfully created, shows on invoice but not visible in bank rec page. Disabled for now, and removed Xero online url link from html template.
            date_paid = "{}-{}-{}".format(year_due, month_due, day_due)
            create_payment(invoice_id, date_paid, total)
            # For the html multiline environment variable, wrap with single quotes, escape single quotes with a backslash and double-up the curley brackets.
            message_paid_html = os.getenv('MESSAGE_PAID_HTML')
            html = message_paid_html.format(
                fname, total_str, invoice_number)
            cc = get_secondary_emails(
                xero_tenant_id, contact_number)
            invoice_pdf_path = get_invoice_pdf(invoice_id)
            message = create_message_with_attachment(
                sender_name, sender_email, email_address, cc, subject, fname, invoice_number, invoice_pdf_path, html)
            service = gmail_creds()
            send_message(service, gmail_api_username, message)
            print('Message sent')
        else:
            message_unpaid_html = os.getenv('MESSAGE_UNPAID_HTML')
            html = message_unpaid_html.format(
                fname, total_str, invoice_number)
            cc = get_secondary_emails(
                xero_tenant_id, contact_number)
            invoice_pdf_path = get_invoice_pdf(invoice_id)
            message = create_message_with_attachment(
                sender_name, sender_email, email_address, cc, subject, fname, invoice_number, invoice_pdf_path, html)
            service = gmail_creds()
            send_message(service, gmail_api_username, message)
            print('Message sent')

    print('-----------------------------------')


@xero_token_required
def get_invoice_pdf(invoice_id):
    xero_tenant_id = get_xero_tenant_id()
    accounting_api = AccountingApi(api_client)
    invoice_pdf_path = accounting_api.get_invoice_as_pdf(
        xero_tenant_id, invoice_id=invoice_id)
    return invoice_pdf_path


@xero_token_required
def create_payment(invoice_id, date_paid, amount_paid):
    bank_account_id = os.getenv('BANK_ACCOUNT_ID')
    if not bank_account_id:
        print("Error: bank_account_id is not defined.")
        return
    xero_tenant_id = get_xero_tenant_id()
    accounting_api = AccountingApi(api_client)
    payment = {
        "Invoice": {"InvoiceID": invoice_id},
        "Account": {"AccountID": bank_account_id},
        "Date": date_paid,
        "Amount": amount_paid
    }
    invoice_payment = accounting_api.create_payment(xero_tenant_id, payment)
    return invoice_payment


@xero_token_required
def get_online_invoice(xero_tenant_id, invoice_id):
    xero_tenant_id = get_xero_tenant_id()
    accounting_api = AccountingApi(api_client)
    invoice_url = accounting_api.get_online_invoice(
        xero_tenant_id, invoice_id)._online_invoices[0].online_invoice_url
    print(invoice_url)
    return invoice_url


@xero_token_required
def get_secondary_emails(xero_tenant_id, contact_number):
    accounting_api = AccountingApi(api_client)
    secondary_contact_persons = accounting_api.get_contact_by_contact_number(
        xero_tenant_id, contact_number)._contacts[0].contact_persons
    secondary_emails = []
    for person in secondary_contact_persons:
        email_address = person.email_address
        secondary_emails.append(email_address)
    if secondary_emails:
        print('cc: {}'.format(secondary_emails))
        secondary_emails = serialize(secondary_emails)
    return secondary_emails


if __name__ == '__main__':
    app.run(host="127.0.0.1")
    app.run(port=5000)
