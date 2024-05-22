from google.cloud import pubsub_v1
from api_client.client import gmail_client, APIClient
from utils.config_manager import config
import json

class NotificationProcessor():
    """
    """

    def __init__(self, input_subscription_name:str, output_topic_name:str, last_history_id_filename:str):

        self.subscriber = pubsub_v1.SubscriberClient()
        self.publisher = pubsub_v1.PublisherClient()
        self.last_history_id_filename = last_history_id_filename
        self.input_subscription_path = self.subscriber.subscription_path(project=config.project_id, subscription=input_subscription_name)
        self.output_subscription_path = self.publisher.topic_path(project=config.project_id, topic=output_topic_name)

    def initiate_pull(self):
        # uses 'subscriber' attribute
        streaming_pull_future = self.subscriber.subscribe(subscription=self.input_subscription_path, callback=self.callback)
        print(f"Subscriber pull initiated. Listening for messages on {self.input_subscription_path}..\n")
        # logging.info(f"Notification Processor pull initiated. Listening for messages on {self.subscriber.subscription_path(config.project_id, subscription=self.input_subscription_name)}..\n")

        with self.subscriber:
            try:
                # Blocks rest of code from running so our pull request is continuously active
                streaming_pull_future.result()
            except KeyboardInterrupt:
                print("KEYBOARD INTERRUPT. NO LONGER LISTENING FOR MESSAGES.")
                streaming_pull_future.cancel()  # Trigger shutdown
                streaming_pull_future.result()  # Block until shutdown is complete
    
    def callback(self, message:pubsub_v1.subscriber.message.Message):
        # Decode message from subscription
        decoded_message = message.data.decode('utf-8')
        # Process message
        email_msg = self.process_notification(decoded_msg=decoded_message)
        # Publish message
        self.publish_messages(msg_to_publish=email_msg)
        message.ack()

    def basic_callback(self, message: pubsub_v1.subscriber.message.Message) -> None:
        print(f"Received {message}.")
        message.ack()
    
    
    def process_notification(self, decoded_msg):
        data_dict = json.loads(decoded_msg)
        new_history_id = data_dict['historyId']
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
    
    def publish_messages(self, msg_to_publish):
        # Encode message to be published
        json_data = json.dumps(msg_to_publish)
        encoded_data = json_data.encode('utf-8')
        # Publish message
        future = self.publisher.publish(topic=self.output_subscription_path, data=encoded_data)
        print(f"Published message ID: {future.result()}")
    
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