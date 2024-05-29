from api_client.client import gmail_client
from utils.config_manager import config

class InboxWatcher():
    """
    Publishes notifications from Gmail API to specified Pub/Sub Project and Topic
    
    Attributes:
        topic_id (str): name of topic we will publish notifications to
        api_client (APIClient): client that interacts with Gmail API to monitor inbox
        inbox_label_id (str): ID of the Gmail label we will be monitoring
    """
    def __init__(self, topic_id: str, inbox_label_name:str):
        """
        Constructor for InboxWatcher class
        Parameters:
            topic_id (str): name of topic we will publish notifications to
            inbox_label_name (str): name of the Gmail label we will be monitoring
        """
        self.topic_id = topic_id
        self.inbox_label_name = inbox_label_name
        self.inbox_label_id = self.find_label_id_by_name(labels=gmail_client.users().labels().list(userId='me').execute(),
                                                        label_name='Customer Emails')
        self.watch(inbox_label_id=self.inbox_label_id)

    def watch(self, inbox_label_id:str):
        """
        Calls Gmail API to watch user inbox
        Parameters:
            inbox_label (str): label defining the folder of the user's inbox we will watch
        """
        request = {
            'labelIds': [inbox_label_id],
            'topicName': f"projects/{config.project_id}/topics/{self.topic_id}",
            'labelFilterBehavior': 'INCLUDE'
            }
        execute = gmail_client.users().watch(userId='me', body=request).execute()
        print(execute)

    
    # def find_label_name(self, labels:list, target_id:str):
    #     """
    #     Given the ID of a label, find the name of the label
    #     Parameters:
    #         labels (list): list of dictionary items representing all labels for this Gmail user's inbox
    #         target_id (str): ID of the inbox whose name we wish to identify
    #     """
    #     for label in labels['labels']:
    #         if label['id'] == target_id:
    #             return label['name']
    #     return None
    
    def find_label_id_by_name(self, labels:list, label_name:str):
        """
         Given the name of a label, find its associated ID
         Parameters:
             labels (list): list of dictionary items representing all labels for this Gmail user's inbox
             label_name (str): name of the inbox whose ID we wish to identify
         """
        for label in labels['labels']:
            if label['name'] == label_name:
                return label['id']
        return None

inbox_watcher = InboxWatcher(topic_id="gmail-inbox-topic", inbox_label_name=config.inbox_label_name)
# inbox_name = inbox_watcher.find_label_name(labels=gmail_client.users().labels().list(userId='me').execute(), target_id=config.inbox_label_id)
print(f"Watching Inbox Folder: {inbox_watcher.inbox_label_name} for {config.username}")