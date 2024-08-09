import uuid
import requests
from django.conf import settings

CAMPAY_API_URL = 'https://api.campay.net/v1/payments'
CAMPAY_API_KEY = 'your_campay_api_key'

def generate_external_reference():
    # Generate a unique external reference using UUID
    return str(uuid.uuid4())

def initiate_payment(amount, phone_number, description):
    headers = {
        'Authorization': f'Bearer {CAMPAY_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'amount': amount,
        'phone_number': phone_number,
        'description': description,
        'external_reference': generate_external_reference()
    }
    response = requests.post(CAMPAY_API_URL, json=data, headers=headers)
    return response.json()
