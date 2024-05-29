from google.cloud import pubsub_v1
from api_client.client import gmail_client, APIClient
from utils.config_manager import config
import json

class ProcessingEntity:
    """
    Class defining entity responsible for processing task in application
    Capable of interacting with Google Cloud Pub/Sub - subscribing to subscriptions and posting to topics
    
    Attributes:
        subscriber (pubsub_v1.SubscriberClient): client responsible for pulling messages from Pub/Sub subscriptions
        publisher (pubsub_v1.PublisherClient): client responsible for publishing messages to Pub/Sub topics
        input_subscription_path (str): path to the subscription this entity pulls from
        output_topic_name (str) (optional): name of topic this entity will publish to
        output_topic_path (str) (optional): path to the topic this entity will publish to
        streaming_pull_future (pubsub_v1.StreamingPullFuture): represents this entity's asynchronous pull operation that listens to Pub/Sub subscription
        name (str): name of the class
    """
    
    def __init__(self, input_subscription_name:str, output_topic_name: str = None):
        """
        Constructor for ProcessingEntity class
        Parameters:
            input_subscription_name (str): name of the subscription this entity pulls from
            output_topic_name (str) (optional): name of topic this entity will publish to
        """
        
        self.subscriber = pubsub_v1.SubscriberClient()
        self.publisher = pubsub_v1.PublisherClient()
        self.input_subscription_path = self.subscriber.subscription_path(project=config.project_id, subscription=input_subscription_name)
        self.output_topic_name = output_topic_name
        if output_topic_name:
            self.output_topic_path = self.publisher.topic_path(project=config.project_id, topic=output_topic_name)
        self.streaming_pull_future = None
        self.name = self.__class__.__name__
    
    def initiate_pull(self):
        """
        Initiates asynchronous pull request to subscription specified by self.input_subscription_path
        """
        self.streaming_pull_future = self.subscriber.subscribe(subscription=self.input_subscription_path, callback=self.callback)
        print(f"{self.name} listening for messages on {self.input_subscription_path}.\n")
        # logging.info(f"Notification Processor pull initiated. Listening for messages on {self.subscriber.subscription_path(config.project_id, subscription=self.input_subscription_name)}..\n")

        with self.subscriber:
            # Blocks rest of code from running so our pull request is continuously active
            self.streaming_pull_future.result()
    
    def basic_callback(self, message: pubsub_v1.subscriber.message.Message) -> None:
        """
        Basic callback function that simply acknowledges queued messages - used to clear message queue
        Parameters:
            message (pubsub_v1.subscriber.message.Message): message received from Pub/Sub subscription
        """
        print(f"{self.name}: Received {message}.")
        message.ack()

    def callback(self, message:pubsub_v1.subscriber.message.Message):
        """
        Callback function used to process incoming message from Pub/Sub subcsription 
        Parameters:
            message (pubsub_v1.subscriber.message.Message): message received from Pub/Sub subscription
        """
        try:
            # Deserialize incoming message
            deserialized_message = self.deserialize_incoming_message(message=message)
            # Perform this entity's processing task
            processed_message = self.processing_task(deserialized_message=deserialized_message)
            # Output processed message (optional if this entity is expected to publish to a Pub/Sub topic)
            if self.output_topic_name:
                self.publish_messages(msg_to_publish=processed_message)
            # Acknowledge receipt of message
            message.ack()
        except:
            # If error occurs during callback functions, DO NOT acknolwedge the message, making it remain in the queue
            message.nack()

    def deserialize_incoming_message(self, message:pubsub_v1.subscriber.message.Message):
        """
        Deserializes incoming message from Pub/Sub subscription
        Messages must be encoded in utf-8 when published to topics and routed to subscriptions, meaning we must decode before processing
        Parameters:
            message (pubsub_v1.subscriber.message.Message): message received from Pub/Sub subscription
        """
        decoded_message = message.data.decode('utf-8')
        deserialized_message = json.loads(decoded_message)
        return deserialized_message
    
    def processing_task(self, deserialized_message:pubsub_v1.subscriber.message.Message):
        """
        Executes processing task that is specific to the entity
        To be overriden by subclasses based on their role in processing
        Parameters:
            deserialized_message (pubsub_v1.subscriber.message.Message): Message object already deserialized by self.deserialize_incoming_message
        """
        pass

    def publish_messages(self, msg_to_publish):
        """
        Encodes processed message and publishes to topic specified by self.output_topic_name
        Parameters:
            msg_to_publish: processed message to be encoded and published
        """
        # Encode message to be published
        json_data = json.dumps(msg_to_publish)
        encoded_data = json_data.encode('utf-8')
        # Publish message
        future = self.publisher.publish(topic=self.output_topic_path, data=encoded_data)
        print(f"{self.name} published message ID: {future.result()}\n")

    def shutdown_subscription(self):
        """
        Gracefully shuts down this entity's Pub/Sub subscription
        """
        if self.streaming_pull_future:
            self.streaming_pull_future.cancel()  # Gracefully stop the pull
            self.streaming_pull_future.result()  # Wait for the cancellation to complete
            print(f"{self.name} pull operation stopped.")

    
    
    
    
        