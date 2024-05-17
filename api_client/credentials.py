import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class APICredentials:
    def __init__(self, SCOPES:list):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.SCOPES = SCOPES
        self.credentials_filepath = os.path.join(current_dir, '../config/credentials.json')
        self.token_filepath = os.path.join(current_dir, '../config/token.json')
        self.creds = self.generate_credentials()
        

    def generate_credentials(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        
        # If valid creds already exist, use them 
        if os.path.exists(self.token_filepath) and os.path.getsize(self.token_filepath)>0:
            creds = Credentials.from_authorized_user_file(self.token_filepath, self.SCOPES)
        # If there are no (valid) creds available
        if not creds or not creds.valid:
            # If there are creds and they're just expired, refresh them
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            # If there are no creds at all (i.e. first-time user)
            else:
                creds = self.initialize_authentication()
            # Save credentials to 'token.json' file for next run
            with open(self.token_filepath, "w") as token:
                token.write(creds.to_json())
        return creds
    
    def initialize_authentication(self):
        # Initialize OAuth client
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_filepath, self.SCOPES
        )
        # Initialize user authentication
        new_creds = flow.run_local_server(port=0)
        return new_creds
    
creds = APICredentials(SCOPES=["https://www.googleapis.com/auth/gmail.readonly"])