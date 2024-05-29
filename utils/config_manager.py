class Config:
    """
    Class representing the configuration of this instance of the application
    
    Attributes:
        project_id (str): ID of the Google Cloud project this application is linked to
        inbox_label_id (str): ID of the Gmail inbox label we will be monitoring
    """
    def __init__(self, project_id:str, inbox_label_id:str):
        """
        Constructor for Config class
        Parameters:
            project_id (str): ID of the Google Cloud project this application is linked to
            inbox_label_id (str): ID of the Gmail inbox label we will be monitoring
        """
        self.project_id = project_id
        self.inbox_label_id = inbox_label_id

config = Config(project_id="blitzy-ocr-api", inbox_label_id="Label_4949462187849619681")