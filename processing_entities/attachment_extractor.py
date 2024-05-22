from google.cloud import pubsub_v1

class AttachmentExtractor():
    def __init__(self, input_subscription_name:str):
        self.input_subscription_name = input_subscription_name
        self.subscriber = pubsub_v1.SubscriberClient()

    def initiate_pull(self):
        # uses 'subscriber' attribute
        return
    
    def callback(self, message:pubsub_v1.subscriber.message.Message):
        # must decode incoming message
        self.extract_attachment()
        self.download_attachment()
        message.ack()

    def extract_attachment(self):
        return
    
    def download_attachment(self):
        return 
