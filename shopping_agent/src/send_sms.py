import requests
from datetime import datetime
# import schedule
import time



def send_text_message(phone_number, message):
    # Set your Twilio account credentials
    account_sid = 'your_account_sid'
    auth_token = 'your_auth_token'

    client = requests.Session()
    client.auth = (account_sid, auth_token)

    url = 'https://api.twilio.com/2010-04-01/Accounts/' + account_sid + '/Messages.json'

    # Create a dictionary to hold the data for the request
    data = {
        'From': '+1234567890',  # Your Twilio number
        'To': phone_number,
        'Body': message
    }

    # Send the POST request to create a new SMS
    response = client.post(url, data=data)

    # Check if the request was successful
    if response.status_code == 201:
        print('Text message sent successfully.')
    else:
        print('Failed to send text message.')