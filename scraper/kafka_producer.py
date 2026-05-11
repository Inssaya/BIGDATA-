from datetime import datetime, timezone
import json
import time

import yfinance as yf
from kafka import KafkaProducer
from kafka.errors import KafkaError, NoBrokersAvailable

BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC_NAME = "stock_topic"
TICKERS = ["AAPL", "TSLA", "MSFT"]
POLL_INTERVAL_SECONDS = 5


def create_producer():
    return KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        retries=3,
        linger_ms=0,
        request_timeout_ms=5000,
        api_version_auto_timeout_ms=5000,
    )


def fetch_stock_record(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d", interval="1d")
    if data.empty:
        return None

    record = json.loads(data.reset_index().to_json(orient="records", date_format="iso"))[0]
    record["ticker"] = ticker
    record["message_timestamp"] = datetime.now(timezone.utc).isoformat()
    return record


def main():
    producer = None

    while True:
        try:
            if producer is None:
                producer = create_producer()
                print(f"Connected to Kafka at {BOOTSTRAP_SERVERS}")

            for ticker in TICKERS:
                record = fetch_stock_record(ticker)
                if record is None:
                    print(f"No stock data returned for {ticker}")
                    continue

                producer.send(TOPIC_NAME, record)
                producer.flush()
                print(f"Sent {ticker} update to {TOPIC_NAME}")

            time.sleep(POLL_INTERVAL_SECONDS)

        except NoBrokersAvailable:
            print(f"⚠️  Kafka is not available at {BOOTSTRAP_SERVERS}")
            print("Retrying in 5 seconds...")
            if producer is not None:
                producer.close()
                producer = None
            time.sleep(5)
        except KafkaError as error:
            print(f"Kafka error: {error}")
            if producer is not None:
                producer.close()
                producer = None
            time.sleep(5)
        except KeyboardInterrupt:
            print("Stopping Kafka producer.")
            if producer is not None:
                producer.close()
            break
        except Exception as error:
            print(f"Unexpected producer error: {error}")
            if producer is not None:
                producer.close()
                producer = None
            time.sleep(5)


if __name__ == "__main__":
    main()
