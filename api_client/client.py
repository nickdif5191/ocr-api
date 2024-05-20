from googleapiclient.discovery import build
from .credentials import APICredentials, gmail_creds

class APIClient:
    """
    Represents a client that makes calls to a Google API on behalf of our app
    Attributes:
        api_name (str): name of the API to access
        api_version (str): version of the API to access
        api_creds (APICredentials): credentials required to access API 
        client ():
    """
    def __init__(self, api_name:str, api_version:str, api_creds:APICredentials):       
        """
        Constructor for APIClient class
        """ 
        self.api_name = api_name
        self.api_version = api_version
        self.api_creds = api_creds
        self.client = self.create_client()
    
    def create_client(self):
        """
        Default method to create client to access Google APIs.
        Subclasses will override given differing creation protocols.
        """
        return None
    
class GmailClient(APIClient):
    def __init__(self, api_creds:APICredentials, api_name="gmail", api_version="v1"):
        """
        Constructor for GmailClient class
        """ 
        super().__init__(api_name, api_version, api_creds)
    
    def create_client(self):
        """
        Builds API client capable of accessing Gmail API
        """
        client = build(serviceName=self.api_name, version=self.api_version, credentials=self.api_creds)
        return client

gmail_client = GmailClient(api_creds=gmail_creds)


