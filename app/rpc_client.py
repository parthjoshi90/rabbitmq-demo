import pika
from app.config import get_settings
from pika.credentials import PlainCredentials

import uuid


class FibonacciRpcClient(object):

    def __init__(self):
        cr = PlainCredentials(get_settings().rabbit_user, get_settings().rabbit_pass)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=get_settings().rabbit_host, credentials=cr))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=str(n))
        self.connection.process_data_events(time_limit=None)
        return self.response


fibonacci_rpc = FibonacciRpcClient()
