from processing_entities.processing_entity import ProcessingEntity
from google.cloud import pubsub_v1
from api_client.client import gmail_client
import json

class NotificationProcessor(ProcessingEntity):
    """
    Class responsible for processing messages incoming from Gmail inbox
    Subclass of ProcessingEntity
    
    Attributes:
        
        last_history_id_filename (str): name of file containing the last saved history ID for Gmail label we are watching
        
        *** From Super Class ***

        subscriber (pubsub_v1.SubscriberClient): client responsible for pulling messages from Pub/Sub subscriptions
        publisher (pubsub_v1.PublisherClient): client responsible for publishing messages to Pub/Sub topics
        input_subscription_path (str): path to the subscription this entity pulls from
        output_topic_name (str) (optional): name of topic this entity will publish to
        output_topic_path (str) (optional): path to the topic this entity will publish to
        streaming_pull_future (pubsub_v1.StreamingPullFuture): represents this entity's asynchronous pull operation that listens to Pub/Sub subscription
        name (str): name of the class
    """

    def __init__(self, input_subscription_name: str, last_history_id_filename:str, output_topic_name: str = None):
        """
        Constructor for NotificationProcessor class
        Parameters:
            last_history_id_filename (str): name of file containing the last saved history ID for Gmail label we are watching
            input_subscription_name (str): name of the subscription this entity pulls from
            output_topic_name (str) (optional): name of topic this entity will publish to
        """

        super().__init__(input_subscription_name, output_topic_name)
        self.last_history_id_filename = last_history_id_filename
    
    def processing_task(self, deserialized_message: pubsub_v1.subscriber.message.Message):
        """
        Calls functions that, in aggregate, complete this entity's processing task
        Parameters:
            deserialized_message (pubsub_v1.subscriber.message.Message): Message object already deserialized by self.deserialize_incoming_message
        """

        processed_data = self.process_notification(most_recent_history_id=deserialized_message, last_history_id=self.get_last_history_id())
        return processed_data
        
    def process_notification(self, most_recent_history_id:str, last_history_id:str):
        """
        Given the most recent history ID from relevant Gmail label, returns all notification history since last_history_id
        Returns a list of History records
        Parameters:
            most_recent_history_id (str): history ID associated with new notification from relevant Gmail label
            last_history_id (str): last saved history ID for relevant Gmail label
        """

        new_history_id = most_recent_history_id['historyId']
        # Get historyId from the previous notification
        # last_history_id = self.get_last_history_id()
        # Store current historyId for future use
        self.store_history_id(historyId=new_history_id)
        if last_history_id:
            # Return list of Gmail events since previous notification
            history_response = gmail_client.users().history().list(userId='me', startHistoryId=last_history_id).execute() 
            if 'history' in history_response:
                return history_response['history'] # a list of History records
            else:
                print("No new notifications found.")
        else:
            # logging.info("No previous historyId found.")   
            return None
    
    def store_history_id(self, historyId):
        """
        Stores history ID associated with newest notification from relevant Gmail label
        Parameters:
            historyId: history ID associated with newest notification from relevant Gmail label
        """

        with open(self.last_history_id_filename, mode="w") as file:
            file.write(str(historyId))
    
    def get_last_history_id(self):
        """
        Gets last recorded historyId from last_history_id_filename
        """
        try:
            with open(self.last_history_id_filename, mode="r") as file:
                return file.read().strip()
        except FileNotFoundError:
            return None
        
notification_processor = NotificationProcessor(input_subscription_name="gmail-inbox-topic-sub", 
                                               output_topic_name="gmail-all-notification-topic",
                                               last_history_id_filename="last_history_id.txt")