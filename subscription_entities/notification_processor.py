from subscription_entities.subscription_entity import SubscriptionEntity
from google.cloud import pubsub_v1
from api_client.client import gmail_client
import json

class NotificationProcessor(SubscriptionEntity):
    def __init__(self, input_subscription_name: str, last_history_id_filename:str, output_topic_name: str = None):
        super().__init__(input_subscription_name, output_topic_name)
        self.last_history_id_filename = last_history_id_filename
    
    def processing_task(self, deserialized_message: pubsub_v1.subscriber.message.Message):
        processed_data = self.process_notification(deserialized_message=deserialized_message)
        return processed_data
        
    def process_notification(self, deserialized_message):
        new_history_id = deserialized_message['historyId']
        # Get historyId from the previous notification
        last_history_id = self.get_last_history_id()
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