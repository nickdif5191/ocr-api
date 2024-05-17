from googleapiclient.discovery import build
from .credentials import APICredentials, creds

class APIClient:
    """
    Represents a client that makes calls to a Google API on behalf of our app
    """
    def __init__(self, api_name:str, api_version:str, api_creds:APICredentials):        
        self.api_version = api_version
        self.api_name = api_name
        self.api_creds = api_creds
        self.client = self.create_client()
    
    def create_client(self):
        """
        Default method to create client to access Google APIs, based on Gmail API syntax.
        Subclasses may override given differing creation protocols.
        """
        client = build(serviceName=self.api_name, version=self.api_version, credentials=self.api_creds)
        return client

gmail_client = APIClient(api_name="gmail", api_version="v1", api_creds=creds.creds)


