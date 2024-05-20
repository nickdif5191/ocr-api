import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

current_dir = os.path.dirname(os.path.abspath(__file__))

class APICredentials:
    """
    Class defining credentials needed for API Client to access the API on behalf of our app
    Attributes:
        SCOPES (str): Access level we are requesting (e.g. read only)
        credentials_filepath (str): filepath of JSON file containing Client ID and Client Secret for our app
        token_filepath (str): filepath of JSON file containing access token and refresh token for user

    """
    def __init__(self, SCOPES:list):
        """
        Constructor for APICredentials class
        Parameters:
            SCOPES (str): Access level we are requesting (e.g. read only)
        """
        self.SCOPES = SCOPES
        self.credentials_filepath = os.path.join(current_dir, '../config/credentials.json')
        self.token_filepath = os.path.join(current_dir, '../config/token.json')
        self.creds = self.generate_credentials()
        

    def generate_credentials(self):
        """
        Utilizes credentials.json and token.json to create credentials for our app
        If no user authentication created yet, calls initialize_authentication to create tokens
        """
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
        """
        Prompts user to authenticate access, generating access and refresh tokens
        """
        # Initialize OAuth client
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_filepath, self.SCOPES
        )
        # Initialize user authentication
        new_creds = flow.run_local_server(port=0)
        return new_creds
    
gmail_creds = APICredentials(SCOPES=["https://www.googleapis.com/auth/gmail.readonly"]).creds