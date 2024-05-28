from concurrent.futures import ThreadPoolExecutor
from api_client.client import gmail_client
from processing_entities.inbox_watcher import inbox_watcher
from subscription_entities.notification_processor import notification_processor
from subscription_entities.notification_filter import notification_filter
from subscription_entities.attachment_extractor import attachment_extractor

entities = []
entities.append(notification_processor)
entities.append(notification_filter)
entities.append(attachment_extractor)

executor = ThreadPoolExecutor(max_workers=len(entities))

# def initiate_task(entity):
with executor:
    futures = []
    # futures = [executor.submit(entity.initiate_pull) for entity in entities] 
    for entity in entities:
        print(f"{entity.__class__.__name__} initialized\n")
        future = executor.submit(entity.initiate_pull)
        futures.append(future)
    
    try:
        for future in futures:
            future.result()
    except KeyboardInterrupt:
        print("Interrupted by user")
        for entity in entities:
            entity.shutdown()

print("Executor shut down.")

    

# if gmail_client:
#     print(f"Gmail Client initialized\n")
#     # labels = gmail_client.users().labels().list(userId="me").execute()
#     # print(labels)
# if inbox_watcher:
#     print(f"Inbox Watcher initialized")
#     inbox_watcher.watch(inbox_label=inbox_watcher.inbox_label)
#     print("\n")
# if notification_processor:
#     print(f"Notification Processor initialized")
#     notification_processor.initiate_pull()
#     print("\n")
# if notification_filter:
#     print("Notification Filter initialized")
#     notification_filter.initiate_pull()
#     print("\n")
# if attachment_extractor:
#     print("Attachment Extractor initialized")
#     attachment_extractor.initiate_pull()
#     print("\n")    
