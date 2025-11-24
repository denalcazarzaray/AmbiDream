"""
Google Calendar API Integration
"""
import os
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build 
from googleapiclient.errors import HttpError
from django.conf import settings


class GoogleCalendarService:
    """
    Service class for Google Calendar API operations
    """
    SCOPES = settings.GOOGLE_CALENDAR_SCOPES

    def __init__(self, user_profile=None):
        """
        Initialize the service with optional user profile
        Args:
         user_profile: UserProfile instance with google credentials
        """
        self.user_profile = user_profile
        self.service = None

    def get_credentials(self):
        """
        Get or refresh Google Calendar credentials
        Returns:
         Credentials object or None
        """
        creds = None

        #Load from user profile if available 
        if self.user_profile and self.user_profile.google_refresh_token:
            try:
                creds = pickle.loads(self.user_profile.google_refresh_token.encode('latin1'))
            except Exception as e:
                print(f"Error loading credentials: {e}")

        #Check if credentials are valid 
        if creds and creds.valid:
            return creds

        #Refresh if expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                #Save refreshed credentials 
                if self.user_profile:
                    self.user_profile.google_refresh_token = pickle.dumps(creds).decode('latin1')
                    self.user_profile.save()
                return creds
            except Exception as e:
                print(f"Error refreshing credentials: {e}")

        #Otherwise, need to re-authenticate 
        return None

    def authenticate(self):
        """
        Authenticate with Google Calendar API
        Returns:
            Credentials object
        """
        creds_file = settings.GOOGLE_CALENDAR_CREDENTIALS_FILE

        if not os.path.exists(creds_file):
            raise FileNotFoundError(
                f"Google credentials file not found at {creds_file}. "
                "Please download it from Google Cloud Console."
            )

        flow = InstalledAppFlow.from_client_secrets_file(creds_file, self.SCOPES)
        creds = flow.run_local_server(port=0)

        #Save credentials to user profile
        if self.user_profile:
            self.user_profile.google_refresh_token = pickle.dumps(creds).decode('latin1')
            self.user_profile.google_calendar_enabled = True
            self.user_profile.save()

        return creds

    def get_service(self):
        """
        Get or create Google Calendar service instance
        Returns:
         Google Calendar service object
        """
        if self.service:
            return self.service

        creds = self.get_credentials()
        if not creds:
            creds = self.authenticate()

        try:
            self.service = build('calendar', 'v3', credentials=creds)
            return self.service
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def create_sleep_event(self, sleep_session):
        """
        Create a sleep event in Google Calendar
        Args:
         sleep_session: SleepSession model instance

        Returns:
         Event ID or None
        """
        service = self.get_service()
        if not service:
            return None

        try:
            event = {
                'summary': f"Sleep ({sleep_session.duration_hours}h)",
                'description': f"Sleep Quality: {sleep_session.get_quality_rating_display() if getattr(sleep_session, 'quality_rating', None) else 'Not rated'}\n"
                               f"Notes: {sleep_session.notes}",
                'start': {
                    'dateTime': sleep_session.sleep_time.isoformat(),
                    'timeZone': self.user_profile.timezone if self.user_profile else 'UTC',
                },
                'end': {
                    'dateTime': sleep_session.wake_time.isoformat(),
                    'timeZone': self.user_profile.timezone if self.user_profile else 'UTC',
                },
                'colorId': '9',
                'transparency': 'transparent',  # Don't show as busy
            }

            event_result = service.events().insert(calendarId='primary', body=event).execute()
            return event_result.get('id')

        except HttpError as error:
            print(f"An error occurred creating event: {error}")
            return None

    def update_sleep_event(self, event_id, sleep_session):
        """
        Update an existing sleep event in Google Calendar
        Args:
         event id: Google Calendar event ID
        sleep session: SleepSession model instance
        Returns:
         Updated event ID or None
        """
        service = self.get_service()
        if not service:
            return None

        try:
            event = {
                'summary': f"Sleep ({sleep_session.duration_hours}h)",
                'description': f"Sleep Quality: {sleep_session.get_quality_rating_display() if getattr(sleep_session, 'quality_rating', None) else 'Not rated'}\n"
                               f"Notes: {sleep_session.notes}",
                'start': {
                    'dateTime': sleep_session.sleep_time.isoformat(),
                    'timeZone': self.user_profile.timezone if self.user_profile else 'UTC',
                },
                'end': {
                    'dateTime': sleep_session.wake_time.isoformat(),
                    'timeZone': self.user_profile.timezone if self.user_profile else 'UTC',
                },
                'colorId': '9',
                'transparency': 'transparent',
            }

            event_result = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            return event_result.get('id')

        except HttpError as error:
            print(f"An error occurred updating event: {error}")
            return None

    def delete_sleep_event(self, event_id):
        """
        Delete a sleep event from Google Calendar
        Args:
         event id: Google Calendar event ID
        Returns:
         True if successful, False otherwise
        """
        service = self.get_service()
        if not service:
            return False

        try:
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            return True
        except HttpError as error:
            print(f"An error occurred deleting event: {error}")
            return False

    def list_upcoming_events(self, max_results=10):
        """
        List upcoming calendar events
        Args:
         max_results: Maximum number of events to return
        Returns:
         List of events or empty list
        """
        service = self.get_service()
        if not service:
            return []

        try:
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            return events_result.get('items', [])

        except HttpError as error:
            print(f"An error occurred listing events: {error}")
            return []
