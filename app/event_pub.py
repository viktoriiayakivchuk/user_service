import json
import pika
from app.core.config import settings
from app.tracing_client import tracing_client

try:
    from opentelemetry.trace import StatusCode
    OTEL_TRACE_OK = True
except ImportError:
    OTEL_TRACE_OK = False

class EventPublisherComponent:
    def __init__(self):
        self.url = settings.RABBITMQ_URL

    def publish_user_registered(self, user_id: str, email: str, role: str, created_at: str = None):
        tracer = tracing_client.get_tracer()
        with tracer.start_as_current_span("rabbitmq.publish_user_registered") as span:
            span.set_attribute("messaging.system", "rabbitmq")
            span.set_attribute("messaging.destination", "user.events")
            span.set_attribute("messaging.routing_key", "user.events.v1.registered")
            
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
                
                # Inject trace context into message headers
                headers = {}
                tracing_client.inject_trace_context(headers)
                
                routing_key = "user.events.v1.registered"
                channel.basic_publish(
                    exchange=exchange_name,
                    routing_key=routing_key,
                    body=json.dumps(payload),
                    properties=pika.BasicProperties(
                        content_type="application/json",
                        delivery_mode=2,
                        headers=headers
                    )
                )
                connection.close()
                print(f"[RabbitMQ] Event {routing_key} successfully published with trace context {headers}.")
                span.set_attribute("messaging.rabbitmq.publish.success", True)
            except Exception as e:
                print(f"[RabbitMQ Error] Failed to publish event: {e}")
                span.record_exception(e)
                if OTEL_TRACE_OK:
                    span.set_status(StatusCode.ERROR, str(e))
                span.set_attribute("messaging.rabbitmq.publish.success", False)

event_publisher = EventPublisherComponent()
