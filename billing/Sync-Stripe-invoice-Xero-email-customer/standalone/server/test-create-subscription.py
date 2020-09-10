import stripe
import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Setup Stripe python client library
env_path = Path(r'C:\Users\Test\secrets\itsolver\automation\billing') / '.env'
load_dotenv(dotenv_path=env_path)
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
response = stripe.Subscription.create(
    customer="cus_HdJIyps5W3VUJX",
    items=[
        {"price": "plan_gsuite-business"},
        {"price": "price_0H14oEGwvziWDQizqWFTb0tc"},
    ],
)
print(response)
