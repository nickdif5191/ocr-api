import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class APICredentials:
    def __init__(self, SCOPES:list):
        self.SCOPES = SCOPES
        self.creds = self.generate_credentials()
        

    def generate_credentials(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        
        # If valid creds already exist, use them 
        if os.path.exists("token.json") and os.path.getsize("token.json")>0:
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
        # If there are no (valid) creds available
        if not creds or not creds.valid:
            # If there are creds and they're just expired, refresh them
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            # If there are no creds at all (i.e. first-time user)
            else:
                creds = self.initialize_authentication()
            # Save credentials to 'token.json' file for next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return creds
    
    def initialize_authentication(self):
        # Initialize OAuth client
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", self.SCOPES
        )
        # Initialize user authentication
        new_creds = flow.run_local_server(port=0)
        return new_creds