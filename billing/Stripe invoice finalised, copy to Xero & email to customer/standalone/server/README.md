# Subscriptions with metered usage

## Requirements## Requirements

- Python 3
- [Stripe CLI](https://stripe.com/docs/stripe-cli)
- [Configured .env file](../README.md)

## How to run

1. Create and activate a new virtual environment

**MacOS / Unix**

```
python3 -m venv env
source env/bin/activate
```

**Windows (PowerShell)**

```
python3 -m venv env
.\env\Scripts\activate.bat
```

2. Install dependencies

```
pip install -r requirements.txt
```

3. Export and run the application

4. While in development, use Stripe CLI to forward events to your local webhook so you don't have to worry about port forwarding etc.

```
stripe listen --forward-to localhost:5000/stripe-webhook
```

**MacOS / Unix**

```
export FLASK_APP=server.py
python3 -m flask run --port=5000
```

**Windows (PowerShell)**

```
$env:FLASK_APP=“server.py"
python3 -m flask run --port=5000
```

4. Go to `localhost:5000` in your browser to see the demo
