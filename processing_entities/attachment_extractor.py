from google.cloud import pubsub_v1
from processing_entities.processing_entity import ProcessingEntity
from api_client.client import gmail_client
import base64

class AttachmentExtractor(ProcessingEntity):
    """
    Class responsible for extracting attachments from emails
    
    Attributes:
        *** From Super Class ***

        subscriber (pubsub_v1.SubscriberClient): client responsible for pulling messages from Pub/Sub subscriptions
        publisher (pubsub_v1.PublisherClient): client responsible for publishing messages to Pub/Sub topics
        input_subscription_path (str): path to the subscription this entity pulls from
        output_topic_name (str) (optional): name of topic this entity will publish to
        output_topic_path (str) (optional): path to the topic this entity will publish to
        streaming_pull_future (pubsub_v1.StreamingPullFuture): represents this entity's asynchronous pull operation that listens to Pub/Sub subscription
        name (str): name of the class

    """
    def __init__(self, input_subscription_name: str, output_topic_name: str = None):
        """
        Constructor for AttachmentExtractor class
        Parameters:
            input_subscription_name (str): name of the subscription this entity pulls from
            output_topic_name (str) (optional): name of topic this entity will publish to
        """
        super().__init__(input_subscription_name, output_topic_name)

    def processing_task(self, deserialized_message:list):
        """
        Calls functions that, in aggregate, complete this entity's processing task
        Parameters:
            deserialized_message (list): Message object already deserialized by self.deserialize_incoming_message
        """
        processed_data = self.extract_and_output_attachments(relevant_messages=deserialized_message)
        return processed_data
    
    def extract_and_output_attachments(self, relevant_messages:list):
        """
        Given a list of email messages, extracts and outputs attachments from them
        Parameters:
            relevant_messages (list): list of email messages to extract attachments from 
        """
        if relevant_messages:
            for email in relevant_messages:
                msg_parts = self.get_message_parts(email=email) 
                parts_w_attachments = 0
                for part in msg_parts:
                    if part['filename']:
                        parts_w_attachments += 1
                        attachment_data = self.get_attachment_data(attachment_content=part, msg_id=email)
                        self.output_attachment(attachment_data=attachment_data, output_loc='attachments', filename=part['filename']) 
                if parts_w_attachments == 0:
                    print(f"{self.name} no attachments in this message\n") 
        else:
            print("No new messages are relevant")
    
    def get_message_parts(self, email):
        """
        Takes in a notification and extracts the associated email message's payload - a list of individual parts of the message content
        Parameters:
            email: object corresponding to the notification type deemed relevant (e.g. relevant_notification_type='labelAdded', notification=LabelAdded object)
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

    def get_attachment_data(self, attachment_content, msg_id:str):
        """
        Given a piece of content containing an attachment, isolate and extract the attachment's identifying data
        Parameters:
            attachment_content: a piece of content from a message representing an attachment file
            msg_id (str): the ID of the message containing the attachment
        """
        # Attachments can be represented 1 of 2 ways, handle both of them
        if 'data' in attachment_content['body']: 
            attachment_data = attachment_content['body']['data']
        else:
            attachment_id = attachment_content['body']['attachmentId']
            attachment = gmail_client.users().messages().attachments().get(userId='me', messageId=msg_id, id=attachment_id).execute()
            attachment_data = attachment['data']

        return attachment_data
    
    def output_attachment(self, attachment_data:str, output_loc:str, filename:str):
        """
        Given an attachment's identifying data, output to appropriate location
        Parameters:
            attachment_data (str): string representing attachment we will output
            output_loc (str): directory location where we will output the attachment
            filename (str): filename of attachment we will output
        """

        # Decode the base64url encoded attachment data
        file_data = base64.urlsafe_b64decode(attachment_data.encode('UTF-8'))
        # Save the file
        path = f"{output_loc}/{filename}"
        with open(path, 'wb') as f:
            f.write(file_data)
        # logging.info(f"Attachment {filename} saved to {path}")
        print(f"{self.name} attachment {filename} saved to {path}\n")

attachment_extractor = AttachmentExtractor(input_subscription_name="gmail-relevant-notification-topic-sub")