import pika
from consumer.config import get_settings
from pika.credentials import PlainCredentials
from consumer.schemas import Data


def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)


class BasicMessageReceiver:
    def __init__(self, username, password, host):
        cr = PlainCredentials(username, password)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, credentials=cr))
        self.channel = self.connection.channel()
    
    def declare_queue(self, queue_name):
        print(f"Trying to declare queue({queue_name})...")
        self.channel.queue_declare(queue=queue_name)

    def get_message(self, ch, method, properties, body):
        print(" [x] Received %r" % body)
    
    def consume_messages(self, queue):
        self.channel.basic_consume(queue=queue, on_message_callback=self.get_message, auto_ack=True)

    def on_request(self, ch, method, props, body):
        n = int(body)

        print(f" [.] fibonacci({n})")
        response = fibonacci(n)
        data = Data(input=n, output=int(response), correlation_id=props.correlation_id)

        self.channel.basic_publish(exchange='',
                        routing_key=props.reply_to,
                        properties=pika.BasicProperties(correlation_id = \
                                                            props.correlation_id),
                        body=data.model_dump_json())
        self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def reply_message(self, queue):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=queue, on_message_callback=self.on_request, auto_ack=False)

    def close(self):
        self.channel.close()
        self.connection.close()


if __name__ == "__main__":

    # Create Basic Message Receiver which creates a connection and channel for consuming messages.
    settings = get_settings()
    basic_message_receiver = BasicMessageReceiver(settings.rabbit_user, settings.rabbit_pass, settings.rabbit_host)
    basic_message_receiver.declare_queue(settings.queue_name)
    basic_message_receiver.declare_queue(settings.rpc_queue)

    basic_message_receiver.consume_messages(settings.queue_name)
    basic_message_receiver.reply_message(settings.rpc_queue)

    try:
        # Consume multiple messages in an event loop.
        print(' [*] Waiting for messages. To exit press CTRL+C')
        basic_message_receiver.channel.start_consuming()
        
    except Exception as e:
        print("Exception>>>>>>>>>>", str(e))
    finally:
        # Close connections.
        basic_message_receiver.close()