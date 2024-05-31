from concurrent.futures import ThreadPoolExecutor
from api_client.client import gmail_client
from inbox_watcher.inbox_watcher import inbox_watcher
from processing_entities.notification_receiver import notification_receiver
from processing_entities.notification_filter import notification_filter
from processing_entities.attachment_extractor import attachment_extractor
import pretty_errors

entities = []
entities.append(notification_receiver)
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
            entity.shutdown_subscription()

print("Executor shut down.")

