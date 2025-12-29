import json
import os
import logging
from functools import lru_cache
from kafka import KafkaProducer

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger("producer")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")


def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers=[KAFKA_BOOTSTRAP],
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
        
    )

def json_deserializer(value):
    return json.dumps(value).encode("utf-8")


def send_message(topic: str, message: dict):
    prod = get_kafka_producer()
    prod.send(topic, message)
    prod.flush()
    log.info(f"Sent to Kafka topic={topic}, message={message}")