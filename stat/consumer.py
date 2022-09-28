import time
import os
import json
import pika
import services
from utils import DecimalEncoder
from models import Page
from dotenv import load_dotenv


load_dotenv()


RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
STAT_SERVICE_QUEUE = os.getenv("STAT_SERVICE_QUEUE")


CONTENT_TYPES = {
    "create_page": services.create_new_page,
    "update_page": services.update_page,
    "delete_page": services.delete_page,
    "get_stat": services.get_pages,
    "new_like": services.new_like,
    "new_follower": services.new_follower,
    "new_follow_request": services.new_follow_request,
    "undo_like": services.undo_like,
    "undo_follower": services.undo_follower,
    "undo_follow_request": services.undo_follow_request
}

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=RABBITMQ_HOST, credentials=credentials))

channel = connection.channel()

channel.queue_declare(queue=STAT_SERVICE_QUEUE)


def callback(ch, method, props, body):
    data = json.loads(body)
    content_type = props.content_type
    if content_type in CONTENT_TYPES:
        service = CONTENT_TYPES[content_type]
        if content_type == "create_page":
            data, stat = service(Page.parse_obj(data))
        elif content_type == "delete_page":
            data, stat = service(data["user_id"], data["id"])
        elif content_type == "update_page":
            data, stat = service(data["name"], data["user_id"], data["id"])
        elif content_type == "get_stat":
            data, stat = service(data["user_id"])
        else:
            data, stat = service(data["id"])
            
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(
                         correlation_id=props.correlation_id),
                     body=json.dumps(data, cls=DecimalEncoder))

    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_message_callback=callback, queue=STAT_SERVICE_QUEUE)
channel.start_consuming()
