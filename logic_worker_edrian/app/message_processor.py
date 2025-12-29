import logging
from shared_edrian.models.data_base import SessionLocal
from shared_edrian.models.models import RequestStatus
from logic_worker_edrian.app.ai_service import AIService

log = logging.getLogger("message_processor")
log.setLevel(logging.WARNING)

class MessageProcessor:
    def __init__(self):
        self.ai_service = AIService()

    def process_request(self, text: str) -> str:
        log.info(f"Processing request: {text}")
        return self.ai_service.generate_response(text)

    def handle_message(self, message_data: dict):
        try:
            request_id = message_data["request_id"]
            text = message_data["text"]

            log.info(f"Received request {request_id}: {text}")

            result = self.process_request(text)

            with SessionLocal() as db:
                db_request = db.query(RequestStatus).filter(RequestStatus.id == request_id).first()
                if db_request:
                    db_request.status = "done"
                    db_request.result = result
                    db.commit()
                    log.info(f"Completed request {request_id}")
                else:
                    log.warning(f"Request {request_id} not found in database")

        except Exception as e:
            log.error(f"Error handling message: {e}")
