from api_client.client import gmail_client
from pubsub_interaction.publisher import gmail_publisher
from pubsub_interaction.subscriber import gmail_subscriber
# from App.email_processing.notification_processor import gmail_notification_processor
# from App.email_processing.attachment_extractor import attachment_extractor

print(f"Gmail Client initialized: {gmail_client}")
print(f"Gmail Publisher initialized: {gmail_publisher}")
print(f"Gmail Subscriber initialized: {gmail_subscriber}")
gmail_subscriber.initiate_pull()