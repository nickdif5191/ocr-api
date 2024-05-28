from google.cloud import pubsub_v1
from api_client.client import gmail_client, APIClient
from utils.config_manager import config
import json

class SubscriptionEntity:
    
    def __init__(self, input_subscription_name:str, output_topic_name: str = None):
        """
        Parameters:
            input_subscription_name (str): name of the subscription this entity pulls from
            output_topic_name (str, optional): name of topic this entity will publish to
        """
        self.subscriber = pubsub_v1.SubscriberClient()
        self.publisher = pubsub_v1.PublisherClient()
        self.input_subscription_path = self.subscriber.subscription_path(project=config.project_id, subscription=input_subscription_name)
        self.output_topic_name = output_topic_name
        if output_topic_name:
            self.output_subscription_path = self.publisher.topic_path(project=config.project_id, topic=output_topic_name)
        self.streaming_pull_future = None
        self.name = self.__class__.__name__
    
    def initiate_pull(self):
        # uses 'subscriber' attribute
        self.streaming_pull_future = self.subscriber.subscribe(subscription=self.input_subscription_path, callback=self.callback)
        print(f"{self.name} listening for messages on {self.input_subscription_path}.\n")
        # logging.info(f"Notification Processor pull initiated. Listening for messages on {self.subscriber.subscription_path(config.project_id, subscription=self.input_subscription_name)}..\n")

        with self.subscriber:
            # Blocks rest of code from running so our pull request is continuously active
            self.streaming_pull_future.result()
    
    def basic_callback(self, message: pubsub_v1.subscriber.message.Message) -> None:
        print(f"{self.name}: Received {message}.")
        message.ack()

    def callback(self, message:pubsub_v1.subscriber.message.Message):
        deserialized_message = self.deserialize_incoming_message(message=message)
        processed_message = self.processing_task(deserialized_message=deserialized_message)
        if self.output_topic_name:
            self.publish_messages(msg_to_publish=processed_message)
        message.ack()

    def deserialize_incoming_message(self, message:pubsub_v1.subscriber.message.Message):
        # Decode message from subscription
        decoded_message = message.data.decode('utf-8')
        deserialized_message = json.loads(decoded_message)
        return deserialized_message
    
    def processing_task(self, deserialized_message:pubsub_v1.subscriber.message.Message):
        """
        Executes processing task that is specific to the entity
        """
        pass

    def publish_messages(self, msg_to_publish):
        # Encode message to be published
        json_data = json.dumps(msg_to_publish)
        encoded_data = json_data.encode('utf-8')
        # Publish message
        future = self.publisher.publish(topic=self.output_subscription_path, data=encoded_data)
        print(f"{self.name} published message ID: {future.result()}\n")

    def shutdown(self):
        if self.streaming_pull_future:
            self.streaming_pull_future.cancel()  # Gracefully stop the pull
            self.streaming_pull_future.result()  # Wait for the cancellation to complete
            print(f"{self.name} pull operation stopped.")

    
    
    
    
        