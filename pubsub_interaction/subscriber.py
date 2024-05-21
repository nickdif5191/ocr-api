from google.cloud import pubsub_v1
from api_client.client import gmail_client
import json

class Subscriber:
    """
    Class designed to pull notifications from a Pub/Sub Subscription
    Attributes:
        project_id (str): Project ID for Google Cloud project
        subscription_id (str): Subscription ID for Google Cloud subscription
    """
    def __init__(self, project_id:str, subscription_id:str, sub_client:pubsub_v1.SubscriberClient):
        """
        Constructor for Subscriber class
        Parameters:
            project_id (str): Project ID for Google Cloud project
            subscription_id (str): Subscription ID for Google Cloud subscription
            sub_client (pubsub_v1.SubscriberClient): Client responsible for generating pull request to Pub/Sub subscription
        """
        self.project_id = project_id
        self.subscription_id = subscription_id
        self.sub_client = sub_client
        self.subscription_path = sub_client.subscription_path(project_id, subscription_id)
    
    def initiate_pull(self):
        """
        Uses sub_client to initiate pull request to subscription at subscription_path
        """
        try:
            # streaming_pull_future = self.sub_client.subscribe(self.subscription_path, callback=self.process_notifications)
            streaming_pull_future = self.sub_client.subscribe(self.subscription_path, callback=self.callback)
            print(f"Subscriber pull initiated. Listening for messages on {self.subscription_path}..\n")
            # logging.info(f"Subscriber pull initiated. Listening for messages on {self.subscription_path}..\n")
        except Exception as e:
            pass   
            # logging.info(f"Failed to start subscriber: {e}")
        with self.sub_client:
            try:
                # When `timeout` is not set, result() will block indefinitely,
                # unless an exception is encountered first.
                streaming_pull_future.result()
            except KeyboardInterrupt:
                print("KEYBOARD INTERRUPT. NO LONGER LISTENING FOR MESSAGES.")
                streaming_pull_future.cancel()  # Trigger the shutdown.
                streaming_pull_future.result()  # Block until the shutdown is complete.

    def callback(self, message: pubsub_v1.subscriber.message.Message):
        """
        Callback function implemented in self.initiate_pull
        Responsible for initial handling of message received at self.subscription_path  
        Acknowledges message if received successfully, does not acknowledge if exception occurs
        Parameters:
            message (message: pubsub_v1.subscriber.message.Message): Message pulled from Pub/Sub Subscription 
        """
        print(message)
        return None

class GmailSubscriber(Subscriber):
    """
    Class designed to pull notifications from Pub/Sub subscription receiving notifications from a Gmail inbox watch

    """

    def __init__(self, project_id:str, subscription_id:str, sub_client:pubsub_v1.SubscriberClient):
        """
        Constructor for GmailSubscriber class
        """
        super().__init__(project_id, subscription_id, sub_client)
        

    def callback(self, message: pubsub_v1.subscriber.message.Message):
        """
        Extracts historyID from notification sent via 'watch' function
        Utilized as callback function in pull request to Subscription
        Acknowledges message if received successfully, does not acknowledge if exception occurs
        Parameters:
            message (message: pubsub_v1.subscriber.message.Message): Message pulled from Pub/Sub Subscription 
        """
        try:
            data = message.data.decode('utf-8')
            data_dict = json.loads(data)
            # Inbox historyId associated with this Pub/Sub notification
            self.new_history_id = data_dict['historyId']
            message.ack()
        except:
            message.nack()


gmail_subscriber = GmailSubscriber()