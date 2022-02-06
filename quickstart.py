from __future__ import print_function

import os
import re
import html
import base64
from datetime import date
from datetime import timedelta
from twilio.rest import Client 

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)

    except HttpError as error:
        print(f'An error occurred: {error}')

    return service


def get_messages(service):
    yesterday = date.today() - timedelta(days = 1)
    print(yesterday)
    query = [f'after:{yesterday} track']
    try:
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = []

        if 'messages' in results:
            messages.extend(results['messages'])
        
        return messages

    except HttpError as error:
        print(f'An error occurred: {error}')


def read_messages(service, messages):
    folder_path = '[YOUR_DIRECTORY_PATH]'
    filename = 'email.txt'
    filepath = os.path.join(folder_path, filename)
    f = open(filepath, 'w')
    f.close()

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()

        payload = msg['payload']
        
        parts = payload.get('parts')
        parse_message(parts, filepath)

    return filepath


def parse_message(parts, filepath):
    if parts:
        for part in parts:
            mimeType = part.get('mimeType')
            body = part.get('body')
            data = body.get('data')
            if part.get('parts'):
                parse_message(part.get('parts'), filepath)
            if mimeType == 'text/html':
                with open(filepath, mode='a') as f:
                    f.write(html.unescape(base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8')))


def search_links(filepath):
    file = open(filepath, 'r')
    text = file.read()
    file.close()
    
    re_ups = 'https?:\/\/www\.ups\.com.*?(?:(?!\").)*'
    re_dhl = 'https?:\/\/del\.dhl\.com.*?(?:(?!\").)*'
    re_ups = re.compile(re_ups)
    re_dhl = re.compile(re_dhl)

    example_results = []
    example_results += re.findall(re_ups, text)
    example_results += re.findall(re_dhl, text)

    links = set()
    if example_results:
        links = set(example_results)
        print(links)

    return links


if __name__ == '__main__':
    service = get_service()
    msg = get_messages(service)
    filepath = read_messages(service, msg)
    links = search_links(filepath)

    if links:
        """
        account_sid = '[YOUR_ACCOUNT_SID]' 
        auth_token = '[YOUR_AUTH_TOKEN]' 
        client = Client(account_sid, auth_token) 
        
        for link in links:
            message = client.messages.create( 
                                        from_='whatsapp:+14155238886',  
                                        body=f'Your order has been shipped! Track it: {link}',      
                                        to='whatsapp:[YOUR_PHONE_NUMBER]' 
                                    ) 

        """
    else:
        print('No tracking links found')