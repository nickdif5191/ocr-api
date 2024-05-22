from api_client.client import gmail_client
from processing_entities.inbox_watcher import inbox_watcher
from processing_entities.notification_processor import notification_processor
from processing_entities.notification_filter import notification_filter

if gmail_client:
    print(f"Gmail Client initialized\n")
    # labels = gmail_client.users().labels().list(userId="me").execute()
    # print(labels)
if inbox_watcher:
    print(f"Inbox Watcher initialized")
    inbox_watcher.watch(inbox_label=inbox_watcher.inbox_label)
    print("\n")
if notification_processor:
    print(f"Notification Processor initialized")
    notification_processor.initiate_pull()
    print("\n")
if notification_filter:
    print("Notification Filter initialized")
    notification_filter.initiate_pull()
    print("\n")
