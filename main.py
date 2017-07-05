# Derivative work of the code in the following tutorial:
# https://developers.google.com/google-apps/calendar/quickstart/python

"""Personal app for tracking activities through Google Calendar"""

from __future__ import print_function
import datetime

import httplib2
import dateutil.parser

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    FLAGS = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    FLAGS = None

# If modifying these scopes, delete your previously saved credentials
# at ./private/credential.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = './private/client_secret.json'
APPLICATION_NAME = 'Personal app for tracking activities'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_path = './private/credential.json'

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if FLAGS:
            credentials = tools.run_flow(flow, store, FLAGS)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_calendar_id():
    """Returns the calendar-id"""
    # See <https://docs.simplecalendar.io/find-google-calendar-id/>
    return open("./private/calendar-id.txt", "rb").read().strip()


def get_hour_rate():
    """Returns the hour rate"""
    return open("./private/hour-rate.txt", "rb").read().strip()


def repr_time(value):
    """ Represent time in a format suitable for the API """
    value = value.isoformat()
    if not value.endswith("Z"):
        value = value + "Z"
    return value


def main():
    """Main function."""

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    time_min_input = "2017-05-01T00:00:00"  # TODO: get from command line
    time_min = dateutil.parser.parse(time_min_input)
    print("time_min:", time_min)

    time_max_input = "2017-06-01T00:00:00"  # TODO: get from command line
    time_max = dateutil.parser.parse(time_max_input)
    print("time_max:", time_max)

    events_result = service.events().list(
        calendarId=get_calendar_id(), timeMin=repr_time(time_min),
        timeMax=repr_time(time_max), singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])

    aggregation = {}
    final_total = datetime.timedelta()
    for event in events:
        summary = event['summary'].strip()
        if not summary.startswith('work'):
            continue
        start = dateutil.parser.parse(
            event['start'].get('dateTime', event['start'].get('date')))
        end = dateutil.parser.parse(
            event['end'].get('dateTime', event['start'].get('date')))
        aggregation.setdefault(summary, datetime.timedelta())
        diff = end - start
        aggregation[summary] += diff
        final_total += diff

    print("---")
    for summary in sorted(aggregation):
        print(summary + ":", aggregation[summary])

    print("---")
    print("total time worked:", final_total)

    hour_rate = float(get_hour_rate())
    amount = (final_total.total_seconds() / 3600.0) * hour_rate
    print("total amount:", amount)

if __name__ == '__main__':
    main()
