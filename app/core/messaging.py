import json
import pika
from app.core.config import settings

class EventPublisher:
    def __init__(self):
        self.url = settings.RABBITMQ_URL

    def publish_user_registered(self, user_id: str, email: str, role: str, created_at: str = None):
        try:
            parameters = pika.URLParameters(self.url)
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            channel.confirm_delivery()

            exchange_name = "user.events"
            channel.exchange_declare(exchange=exchange_name, exchange_type="topic", durable=True)

            payload = {
                "user_id": user_id,
                "email": email,
                "role": role,
                "created_at": created_at
            }
            
            routing_key = "user.events.v1.registered"
            channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=json.dumps(payload),
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=2  
                )
            )
            connection.close()
            print(f"[RabbitMQ] Event {routing_key} successfully published.")
        except Exception as e:
            print(f"[RabbitMQ Error] Failed to publish event: {e}")

event_publisher = EventPublisher()