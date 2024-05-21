from api_client.client import gmail_client
from pubsub_interaction.publisher import gmail_notifier
# from App.pubsub_interaction.subscriber import gmail_subscriber
# from App.email_processing.notification_processor import gmail_notification_processor
# from App.email_processing.attachment_extractor import attachment_extractor

print(f"Gmail Client initialized: {gmail_client}")
print(f"Gmail Notifier initialized: {gmail_notifier}")