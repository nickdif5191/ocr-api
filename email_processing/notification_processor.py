from api_client.client import gmail_client
from pubsub_interaction.subscriber import gmail_subscriber

class NotificationProcessor:
    """
    Class designed to process notifications successfully received by Subscriber objects
    Currently only implemented for notifications from GmailSubscriber objects, but could be used for other Subscriber types
    """
    pass


class GmailNotificationProcessor(NotificationProcessor):
    """
    Class designed to process notifications successfully received from GmailSubscriber class
    Attributes:
        relevant_notification_type (str): The type of notification deemed relevant by this instance (e.g. 'labelsAdded'. 'messagesAdded')
    """
    def __init__(self, relevant_notification_type:str, last_history_id_filename:str):
        """
        Constructor for NotificationProcessor class
        Attributes:
            relevant_notification_type (str): The type of notification deemed relevant by this instance (e.g. 'labelsAdded'. 'messagesAdded')
        """
        self.relevant_notification_type = relevant_notification_type
        self.last_history_id_filename = last_history_id_filename
        
    
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

    def get_all_email_notifications(self, new_history_id:str):
        """
        Gets a comprehensive list of new notifications from Gmail inbox since our last notification
        Note: list includes ALL notifications, which includes internal updates/notifications
        """
        # Get historyId from the previous notification
        last_history_id = self.get_last_history_id()
        # Store current historyId for future use
        self.store_history_id(historyId=new_history_id)
        if last_history_id:
            # Return list of Gmail events since previous notification
            history_response = gmail_client.client.users().history().list(userId='me', startHistoryId=last_history_id).execute() 
            return history_response['history'] # a list of History records
        else:
            # logging.info("No previous historyId found.")   
            return None
        
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
            pass
    
gmail_notification_processor = GmailNotificationProcessor()
"""
# Get comprehensive list of new notifications from Gmail inbox
new_notifications = self.get_all_email_notifications(new_history_id=new_history_id)
relevant_notifications = self.filter_relevant_notifications(new_notifications=new_notifications, notification_type=self.relevant_notification_type)
for notification in relevant_notifications:
    list_message_parts = self.get_message_parts(notification=notification)
"""
    