from processing_entities.processing_entity import ProcessingEntity
from google.cloud import pubsub_v1
from api_client.client import gmail_client
import json

class NotificationFilter(ProcessingEntity):
    """
    Class responsible for identifying Gmail notifications that are relevant to our application
    Subclass of ProcessingEntity
    
    Attributes:

        notification_type (str): the type of notification type we are deeming relevant for our application
    
        *** From Super Class ***

        subscriber (pubsub_v1.SubscriberClient): client responsible for pulling messages from Pub/Sub subscriptions
        publisher (pubsub_v1.PublisherClient): client responsible for publishing messages to Pub/Sub topics
        input_subscription_path (str): path to the subscription this entity pulls from
        output_topic_name (str) (optional): name of topic this entity will publish to
        output_topic_path (str) (optional): path to the topic this entity will publish to
        streaming_pull_future (pubsub_v1.StreamingPullFuture): represents this entity's asynchronous pull operation that listens to Pub/Sub subscription
        name (str): name of the class
    """

    def __init__(self, input_subscription_name: str, notification_type:str, output_topic_name: str = None):
        """
        Constructor for NotificationFilter class
        Parameters:
            notification_type (str): the type of notification type we are deeming relevant for our application
            input_subscription_name (str): name of the subscription this entity pulls from
            output_topic_name (str) (optional): name of topic this entity will publish to
        """
        super().__init__(input_subscription_name, output_topic_name)
        self.notification_type = notification_type
    
    def processing_task(self, deserialized_message:list):
        """
        Calls functions that, in aggregate, complete this entity's processing task
        Parameters:
            deserialized_message (list): Message object already deserialized by self.deserialize_incoming_message
        """

        processed_data = self.filter_relevant_notifications(new_notifications=deserialized_message)
        return processed_data
    
    def filter_relevant_notifications(self, new_notifications:list):
        """
        Filters comprehensive list of notifications to relevant ones
        Parameters:
            new_notifications (list): Comprehensive list of new notifications from Gmail inbox
        """
        if new_notifications:
            relevant_notifications = [item[self.notification_type] for item in new_notifications if self.notification_type in item]
            return relevant_notifications
        else:
            # logging.info("No new notifications observed since previous historyId")
            pass

notification_filter = NotificationFilter(input_subscription_name="gmail-all-notification-topic-sub",
                                         output_topic_name="gmail-relevant-notification-topic",
                                         notification_type='messagesAdded')