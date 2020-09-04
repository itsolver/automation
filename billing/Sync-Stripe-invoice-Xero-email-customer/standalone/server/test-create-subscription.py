import stripe
import os
from dotenv import load_dotenv, find_dotenv

# Setup Stripe python client library
load_dotenv('/Users/angusmclauchlan/.secrets/itsolver/automation/billing/.env')
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

response = stripe.Subscription.create(
    customer="cus_HdJIyps5W3VUJX",
    items=[
        {"price": "plan_gsuite-business"},
        {"price": "price_0H14oEGwvziWDQizqWFTb0tc"},
    ],
)
print(response)
