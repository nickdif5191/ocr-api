from google.cloud import pubsub_v1
from api_client.client import gmail_client
from utils.config_manager import config
import json
import base64

class AttachmentExtractor():
    def __init__(self, input_subscription_name:str):
        self.subscriber = pubsub_v1.SubscriberClient()
        self.input_subscription_path = self.subscriber.subscription_path(project=config.project_id, subscription=input_subscription_name)
        self.subscriber = pubsub_v1.SubscriberClient()

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
    
    def basic_callback(self, message: pubsub_v1.subscriber.message.Message) -> None:
        print(f"Received {message}.")
        message.ack()

    def callback(self, message:pubsub_v1.subscriber.message.Message):
         # Decode message from subscription
        decoded_message = message.data.decode('utf-8')
        deserialized_message = json.loads(decoded_message)
        # Output attachments
        for new_email in deserialized_message:
            msg_parts = self.get_message_parts(email=new_email) 
            for part in msg_parts:
                if part['filename']:
                    attachment_data = self.extract_attachment_data(msg_part=part, msg_id=new_email)
                    self.output_attachment(attachment_data=attachment_data, filename=part['filename'])
        message.ack()

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

    def extract_attachment_data(self, msg_part, msg_id:str):
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
        print(f"Attachment {filename} saved to {path}")

attachment_extractor = AttachmentExtractor(input_subscription_name="gmail-relevant-notification-topic-sub")