import os.path
import base64
import json
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests
from email import message_from_bytes
from email.mime.text import MIMEText  # AGGIUNGI QUESTO IMPORT
from datetime import datetime
from email.utils import formatdate

# Scope per lettura Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def create_reply_message(to: str, subject: str, message_text: str, thread_id: str, original_message_id: str):
    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = f"Re: {subject}"
    message['In-Reply-To'] = original_message_id
    message['References'] = original_message_id
    message['Date'] = formatdate(localtime=True)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {
        'raw': raw_message,
        'threadId': thread_id
    }

def send_reply_email(service, to: str, subject: str, message_text: str, thread_id: str, original_message_id: str):
    message = create_reply_message(to, subject, message_text, thread_id, original_message_id)
    sent_message = service.users().messages().send(userId='me', body=message).execute()
    print(f"📨 Risposta inviata con ID: {sent_message['id']}")
    return sent_message

def get_unread_messages(service):
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
    return results.get('messages', [])

def mark_as_read(service, message_id):
    service.users().messages().modify(
        userId='me',
        id=message_id,
        body={
            'removeLabelIds': ['UNREAD']
        }
    ).execute()
    print(f"✅ Messaggio {message_id} segnato come letto.")


def parse_message(service, msg_id):
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    # mark_as_read(service, msg_id)

    payload = msg['payload']
    headers = payload.get('headers', [])

    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), None)
    raw_sender = next((h['value'] for h in headers if h['name'] == 'From'), "")
    match = re.match(r'^(.*)\s<(.+?)>$', raw_sender)
    if match:
        senderName = match.group(1).strip()
        senderEmail = match.group(2).strip()
    else:
        senderName = ""
        senderEmail = raw_sender.strip()
    date = next((h['value'] for h in headers if h['name'] == 'Date'), None)
    original_message_id = next((h['value'] for h in headers if h['name'] == 'Message-ID'), None)

    parts = payload.get('parts', [])
    text = ""
    for part in parts:
        if part['mimeType'] == 'text/plain':
            data = part['body']['data']
            text = base64.urlsafe_b64decode(data).decode('utf-8')
            break

    return {
        'message_id': msg['id'],
        'thread_id': msg['threadId'],
        'subject': subject,
        'senderName': senderName,
        'senderEmail': senderEmail,
        'date': date,
        'snippet': msg.get('snippet', ''),
        'text': text,
        'original_message_id': original_message_id
    }


if __name__ == '__main__':
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)

    messages = get_unread_messages(service)

    if not messages:
        print("✅ Nessun messaggio non letto.")
    else:
        print(f"📩 {len(messages)} messaggi non letti trovati.")
        for m in messages:
            parsed = parse_message(service, m['id'])
            print(json.dumps(parsed, indent=2))

