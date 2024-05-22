from google.cloud import pubsub_v1

class NotificationFilter:
    def __init__(self, input_subscription_name:str, output_topic_name:str):


    def filter_relevant_notifications(self, new_notifications:list, notification_type:str):
        """
        Filters comprehensive list of notifications to relevant ones
        Parameters:
            new_notifications (list): Comprehensive list of new notifications from Gmail inbox
            notification_type (str): Specific category of notification we wish to identify (e.g. 'messagesAdded', 'labelsAdded')
        """
        if new_notifications:
            if notification_type in new_notifications:
                relevant_notifications = new_notifications[notification_type]
                return relevant_notifications # list of objects corresponding to notification_type (e.g. MessageAdded, LabelAdded, MessageDeleted)
            else:
                # logging.info("No relevant notifications found in new notifications")
                pass
        else:
            # logging.info("No new notifications observed since previous historyId")
            passz