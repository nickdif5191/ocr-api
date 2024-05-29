from subscription_entities.subscription_entity import SubscriptionEntity
from google.cloud import pubsub_v1
from api_client.client import gmail_client
import json

class NotificationFilter(SubscriptionEntity):
    def __init__(self, input_subscription_name: str, notification_type:str, output_topic_name: str = None):
        super().__init__(input_subscription_name, output_topic_name)
        self.notification_type = notification_type
    
    def processing_task(self, deserialized_message:list):
        processed_data = self.filter_relevant_notifications(new_notifications=deserialized_message)
        return processed_data
    
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

notification_filter = NotificationFilter(input_subscription_name="gmail-all-notification-topic-sub",
                                         output_topic_name="gmail-relevant-notification-topic",
                                         notification_type='messagesAdded')