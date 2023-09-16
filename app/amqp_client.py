import pika
from app.config import get_settings
from pika.credentials import PlainCredentials


class BasicMessageSender:

    def __init__(self):
        cr = PlainCredentials(get_settings().rabbit_user, get_settings().rabbit_pass)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=get_settings().rabbit_host, credentials=cr))
        self.channel = self.connection.channel()

    def declare_queue(self, queue_name):
        print(f"Trying to declare queue({queue_name})...")
        self.channel.queue_declare(queue=queue_name)

    def send_message(self, exchange, routing_key, body):
        self.channel.basic_publish(exchange=exchange,
                              routing_key=routing_key,
                              body=body)
        print(f"Sent message. Exchange: {exchange}, Routing Key: {routing_key}, Body: {body}")

    def close(self):
        self.channel.close()
        self.connection.close()