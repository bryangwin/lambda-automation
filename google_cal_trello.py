#!/opt/homebrew/bin/python3

# This script will add upcoming events from your Google Calendar to a Trello board.
# Make sure you have your keys in your .env file and downloaded your credentials.json file from Google.
# This will create a processed_events.txt file in the same directory as this script.

# Author: Bryan Gwin
# Date: Sep 1, 2023

from __future__ import print_function

import datetime
import os.path
import pytz
import requests

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')
TRELLO_LIST_ID = os.getenv('TRELLO_LIST_ID')


def add_to_trello(name):
    url = f"https://api.trello.com/1/cards"
    headers = {
        "Accept": "application/json"
    }
    query = {
       'key': TRELLO_API_KEY,
       'token': TRELLO_TOKEN,
       'idList': TRELLO_LIST_ID,
       'name': name

    }
    response = requests.request(
       "POST",
       url,
       headers=headers,
       params=query
    )
    if response.status_code != 200:
        print(f"Error adding card to Trello: {response.text}")

def load_processed_event_ids(filename="processed_events.txt"):
    """Load previously processed event IDs from a file."""
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return set(f.read().splitlines())
    return set()


def save_processed_event_id(event_id, filename="processed_events.txt"):
    """Save an event ID to a file."""
    with open(filename, "a") as f:
        f.write(event_id + "\n")


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
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
        service = build('calendar', 'v3', credentials=creds)

        pst = pytz.timezone('US/Pacific')
        now_pst = datetime.datetime.now(pst)
        now = now_pst.isoformat()  
        print('Getting the upcoming 15 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=15, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        processed_event_ids = load_processed_event_ids()
        
        for event in events:
            if event['id'] not in processed_event_ids:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(start, event['summary'])
                add_to_trello(name=event['summary'] + start)
                save_processed_event_id(event['id'])

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()