from api_client.client import gmail_client, APIClient
from utils.config_manager import config

class InboxWatcher():
    """
    Publishes notifications from Gmail API to specified Pub/Sub Project and Topic
    """
    def __init__(self, topic_id: str, api_client: APIClient, inbox_label:str):
        self.topic_id = topic_id
        self.api_client = api_client
        self.inbox_label = inbox_label

    def watch(self, inbox_label:str):
        """
        Calls Gmail API to watch user inbox
        Parameters:
            inbox_label (str): label defining the folder of the user's inbox we will watch
        """
        request = {
            'labelIds': [inbox_label],
            'topicName': f"projects/{config.project_id}/topics/{self.topic_id}",
            'labelFilterBehavior': 'INCLUDE'
            }
        execute = self.api_client.users().watch(userId='me', body=request).execute()
        print(execute)

inbox_watcher = InboxWatcher(topic_id="gmail-inbox-topic", api_client=gmail_client, inbox_label="Label_6952034271687541778")