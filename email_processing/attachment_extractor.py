from api_client.client import gmail_client
from email_processing.notification_processor import gmail_notification_processor

class AttachmentExtractor:
    """
    Extracts attachments from relevant Message objects identified by GmailNotificationProcessor
    """
    def __init__(self):
        pass

    def get_message_parts(self, notification):
            """
            Takes in a notification and extracts the associated email message's payload - a list of individual parts of the message content
            Parameters:
                notification: object corresponding to the notification type deemed relevant (e.g. relevant_notification_type='labelAdded', notification=LabelAdded object)
            """
            # Get Message object from notification - represents an actual email message
            message = notification['message']
            # Get ID associated with specific message
            message_id = message['id']
            # Call Gmail API to extract full message associated with message_id
            message_detail = gmail_client.client.users().messages().get(userId='me', id=message_id, format='full').execute()
            # Get the message payload - JSON representing actual content of the message
            message_payload = message_detail.get('payload')
            # Get a list of individual parts representing different components of message content
            message_parts = message_payload['parts']
            return message_parts
    
attachment_extractor = AttachmentExtractor