import os

DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")
TELEGRAM_KEY = os.getenv("TELEGRAM_API_KEY")
print(TELEGRAM_KEY)
users_waiting_questions = set()
user_state = {}
user_topic = None
API_USERNAME = "API_USERNAME "
API_PASSWORD = "API_PASSWORD "
API_EMAIL = "razer4832@gmail.com"