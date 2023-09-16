import json
from fastapi import FastAPI, Query
from app.amqp_client import BasicMessageSender
from app.rpc_client import fibonacci_rpc
from app.config import get_settings
from pydantic import BaseModel


class Message(BaseModel):
    msg: str


app = FastAPI(
    debug=True,
    title="Rabitmq Demo",
    version= '0.1.0'
)


@app.get("/")
def helth():
    return {'msg': "Hello World!"}

@app.post("/publish")
def publish(message: Message):
    settings = get_settings()
    publisher = BasicMessageSender()
    return publisher.send_message(exchange='', routing_key= settings.queue_name, body=message.model_dump_json())

@app.post("/rpc/fib")
def call_fib(num: int):
    print(f" [x] Requesting fib({num})")
    response = fibonacci_rpc.call(num)
    return json.loads(response)