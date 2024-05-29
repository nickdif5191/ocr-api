class Config:
    """
    Class representing the configuration of this instance of the application
    
    Attributes:
        project_id (str): ID of the Google Cloud project this application is linked to
        inbox_label_id (str): ID of the Gmail inbox label we will be monitoring
    """
    def __init__(self, username:str, project_id:str, inbox_label_name:str):
        """
        Constructor for Config class
        Parameters:
            username (str): the username associated with Gmail account - {username}@gmail.com
            project_id (str): ID of the Google Cloud project this application is linked to
            inbox_label_name (str): name of the Gmail inbox label we will be monitoring
        """
        self.username = username
        self.project_id = project_id
        self.inbox_label_name = inbox_label_name

config = Config(username="customer.emails.blitzy", project_id="blitzy-ocr-api", inbox_label_name="Customer Emails")