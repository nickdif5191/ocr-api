from api_client.client import gmail_client, APIClient

class Publisher:
    """
    Class designed to publish notifications inbound from a specified API to specified Pub/Sub Project and Topic
    Attributes:
        project_id (str): Project ID for Google Cloud project that harbors our target topic
        topic_id (str): Topic ID for target topic
        api_client (APIClient): Client responsible for connecting to API and identifying notifications to publish
    """
    def __init__(self, project_id:str, topic_id:str, api_client:APIClient):
        """
        Constructor for Publisher class
        Parameters:
            project_id (str): Project ID for Google Cloud project that harbors our target topic
            topic_id (str): Topic ID for target topic
            api_client (APIClient): Client responsible for connecting to API and identifying notifications to publish
        
        """
        self.project_id = project_id
        self.topic_id = topic_id
        self.api_client = api_client

class GmailPublisher(Publisher):
    """
    Publishes notifications from Gmail API to specified Pub/Sub Project and Topic
    """
    def __init__(self, project_id: str, topic_id: str, api_client: APIClient, inbox_label:str):
        # Call the constructor of the superclass (Publisher) to initialize its attributes
        super().__init__(project_id, topic_id, api_client)
        self.watch(inbox_label=inbox_label)

    def watch(self, inbox_label:str):
        """
        Calls Gmail API to watch user inbox
        Parameters:
            inbox_label (str): label defining the folder of the user's inbox we will watch
        """
        request = {
            'labelIds': [inbox_label],
            'topicName': f"projects/blitzy-ocr-api/topics/gmail-topic",
            'labelFilterBehavior': 'INCLUDE'
            }
        execute = self.api_client.users().watch(userId='me', body=request).execute()
        print(execute)

gmail_publisher = GmailPublisher(project_id="blitzy-ocr-api", topic_id="gmail-topic", api_client=gmail_client, inbox_label="Label_6952034271687541778ß")

if __name__ == "__main__":
    test_gmail_publisher = GmailPublisher(project_id="blitzy-ocr-api", topic_id="gmail-topic", api_client=gmail_client, inbox_label="Label_6952034271687541778ß")
    print(f"Test case initialized: {test_gmail_publisher}")