from google.cloud import pubsub_v1
from subscription_entities.subscription_entity import SubscriptionEntity
from api_client.client import gmail_client
import base64

class AttachmentExtractor(SubscriptionEntity):
    def __init__(self, input_subscription_name: str, output_topic_name: str = None):
        super().__init__(input_subscription_name, output_topic_name)

    def processing_task(self, deserialized_message:list):
        processed_data = self.extract_attachments(relevant_messages=deserialized_message)
        return processed_data
    
    def extract_attachments(self, relevant_messages:list):
        for email in relevant_messages:
            msg_parts = self.get_message_parts(email=email) 
            parts_w_attachments = 0
            for part in msg_parts:
                if part['filename']:
                    parts_w_attachments += 1
                    attachment_data = self.get_attachment_data(msg_part=part, msg_id=email)
                    self.output_attachment(attachment_data=attachment_data, filename=part['filename']) 
            if parts_w_attachments == 0:
                print(f"{self.name} no attachments in this message\n") 
    
    def get_message_parts(self, email):
            """
            Takes in a notification and extracts the associated email message's payload - a list of individual parts of the message content
            Parameters:
                notification: object corresponding to the notification type deemed relevant (e.g. relevant_notification_type='labelAdded', notification=LabelAdded object)
            """
            # Get Message object from notification - represents an actual email message
            message_id = email[0]['message']['id']
            # Get ID associated with specific message
            # message_id = message['id']
            # Call Gmail API to extract full message associated with message_id
            message_detail = gmail_client.users().messages().get(userId='me', id=message_id, format='full').execute()
            # Get the message payload - JSON representing actual content of the message
            message_payload = message_detail.get('payload')
            # Get a list of individual parts representing different components of message content
            message_parts = message_payload['parts']
            return message_parts

    def get_attachment_data(self, msg_part, msg_id:str):
        # Attachments can be represented 1 of 2 ways, handle both of them
        if 'data' in msg_part['body']: 
            attachment_data = msg_part['body']['data']
        else:
            attachment_id = msg_part['body']['attachmentId']
            attachment = gmail_client.users().messages().attachments().get(userId='me', messageId=msg_id, id=attachment_id).execute()
            attachment_data = attachment['data']

        return attachment_data
    
    def output_attachment(self, attachment_data:str, filename:str):
        # Decode the base64url encoded attachment data
        file_data = base64.urlsafe_b64decode(attachment_data.encode('UTF-8'))
        # Save the file
        path = f"attachments/{filename}"
        with open(path, 'wb') as f:
            f.write(file_data)
        # logging.info(f"Attachment {filename} saved to {path}")
        print(f"{self.name} attachment {filename} saved to {path}\n")

attachment_extractor = AttachmentExtractor(input_subscription_name="gmail-relevant-notification-topic-sub")