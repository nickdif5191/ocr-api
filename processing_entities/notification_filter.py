from google.cloud import pubsub_v1
from utils.config_manager import config
import json

class NotificationFilter:
    def __init__(self, input_subscription_name:str, output_topic_name:str, notification_type:str):
        self.subscriber = pubsub_v1.SubscriberClient()
        self.publisher = pubsub_v1.PublisherClient()
        self.input_subscription_path = self.subscriber.subscription_path(project=config.project_id, subscription=input_subscription_name)
        self.output_subscription_path = self.publisher.topic_path(project=config.project_id, topic=output_topic_name)
        self.notification_type = notification_type
        self.streaming_pull_future = None
        self.name = self.__class__.__name__

    def initiate_pull(self):
        # uses 'subscriber' attribute
        self.streaming_pull_future = self.subscriber.subscribe(subscription=self.input_subscription_path, callback=self.callback)
        print(f"{self.name} listening for messages on {self.input_subscription_path}.\n")
        # logging.info(f"Notification Processor pull initiated. Listening for messages on {self.subscriber.subscription_path(config.project_id, subscription=self.input_subscription_name)}..\n")

        with self.subscriber:
            # Blocks rest of code from running so our pull request is continuously active
            self.streaming_pull_future.result()
        
    def shutdown(self):
        if self.streaming_pull_future:
            self.streaming_pull_future.cancel()  # Gracefully stop the pull
            self.streaming_pull_future.result()  # Wait for the cancellation to complete
            print(f"{self.name} pull operation stopped.")

    def callback(self, message:pubsub_v1.subscriber.message.Message):
        # Decode message from subscription
        decoded_message = message.data.decode('utf-8')
        deserialized_message = json.loads(decoded_message)
        # Process message
        email_msg = self.filter_relevant_notifications(new_notifications=deserialized_message)
        # Publish message
        self.publish_messages(msg_to_publish=email_msg)
        message.ack()
    
    def filter_relevant_notifications(self, new_notifications:list):
        """
        Filters comprehensive list of notifications to relevant ones
        Parameters:
            new_notifications (list): Comprehensive list of new notifications from Gmail inbox
            notification_type (str): Specific category of notification we wish to identify (e.g. 'messagesAdded', 'labelsAdded')
        """
        if new_notifications:
            relevant_notifications = [item[self.notification_type] for item in new_notifications if self.notification_type in item]
            return relevant_notifications
        else:
            # logging.info("No new notifications observed since previous historyId")
            pass

    def publish_messages(self, msg_to_publish):
        # Encode message to be published
        json_data = json.dumps(msg_to_publish)
        encoded_data = json_data.encode('utf-8')
        # Publish message
        future = self.publisher.publish(topic=self.output_subscription_path, data=encoded_data)
        print(f"{self.name} published message ID: {future.result()}\n")

notification_filter = NotificationFilter(input_subscription_name="gmail-all-notification-topic-sub",
                                         output_topic_name="gmail-relevant-notification-topic",
                                         notification_type='labelsAdded')

    