import logging
import time
from logic_worker_edrian.app.consumer import get_kafka_consumer
from logic_worker_edrian.app.message_processor import MessageProcessor

log = logging.getLogger("logic_worker_main")
log.setLevel(logging.WARNING)

def run_worker():
    topic = "user_requests"
    processor = MessageProcessor()
    consumer = get_kafka_consumer(topic)

    log.info("Starting logic worker...")
    for msg in consumer:
        try:
            value = msg.value  # already deserialized dict
            processor.handle_message(value)
        except Exception as e:
            log.exception("Error processing message loop: %s", e)
            time.sleep(1)

if __name__ == "__main__":
    run_worker()
