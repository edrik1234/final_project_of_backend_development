import json
import os
import logging
from kafka import KafkaConsumer

log = logging.getLogger("consumer")
log.setLevel(logging.WARNING)

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

def get_kafka_consumer(topic: str, group_id: str = "default_group"):
    return KafkaConsumer(
        topic,
        bootstrap_servers=[KAFKA_BOOTSTRAP],
        group_id=group_id,
       value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

def json_deserializer(value):
    return json.loads(value.decode("utf-8"))