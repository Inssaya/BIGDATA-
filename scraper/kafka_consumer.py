import json
import time

from kafka import KafkaConsumer
from kafka.errors import KafkaError, NoBrokersAvailable

BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC_NAME = "stock_topic"


def create_consumer():
    return KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="stock_topic_consumer",
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        request_timeout_ms=30000,
        session_timeout_ms=10000,
        api_version_auto_timeout_ms=5000,
    )


def main():
    consumer = None

    while True:
        try:
            if consumer is None:
                consumer = create_consumer()
                print(f"Listening on Kafka topic: {TOPIC_NAME}")

            for message in consumer:
                try:
                    print(json.dumps(message.value, indent=2))
                except json.JSONDecodeError:
                    print(message.value)

        except NoBrokersAvailable:
            print(f"⚠️  Kafka is not available at {BOOTSTRAP_SERVERS}")
            print("Retrying in 5 seconds...")
            if consumer is not None:
                consumer.close()
                consumer = None
            time.sleep(5)
        except KafkaError as error:
            print(f"Kafka error: {error}")
            if consumer is not None:
                consumer.close()
                consumer = None
            time.sleep(5)
        except KeyboardInterrupt:
            print("Stopping Kafka consumer.")
            if consumer is not None:
                consumer.close()
            break
        except Exception as error:
            print(f"Unexpected consumer error: {error}")
            if consumer is not None:
                consumer.close()
                consumer = None
            time.sleep(5)


if __name__ == "__main__":
    main()