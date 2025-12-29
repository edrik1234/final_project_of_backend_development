import telebot
import requests
import logging
import bot.app.config as config
import json
from sqlalchemy.orm import Session
from shared_edrian.models.data_base import SessionLocal
from shared_edrian.models.models import TelegramUser
from shared_edrian.models.models import GameSession
import time
import os
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo
API_BASE = "http://api:8000"
TOKEN = None

bot = telebot.TeleBot(config.TELEGRAM_KEY)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("telegram_bot")

# =====================================================
# AUTH
# =====================================================

def api_register():
    resp = requests.post(
        f"{API_BASE}/auth/register",
        json={
            "username": config.API_USERNAME,
            "email": config.API_EMAIL,
            "password": config.API_PASSWORD,
        },
    )

    if resp.status_code in (200, 409):
        return

    raise RuntimeError(f"Register failed: {resp.text}")


def api_login():
    global TOKEN

    resp = requests.post(
        f"{API_BASE}/auth/login",
        data={
            "username": config.API_USERNAME,
            "password": config.API_PASSWORD,
        }, 
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if resp.status_code == 401:
        api_register()
        return api_login()

    if resp.status_code != 200:
        raise RuntimeError(f"Login failed: {resp.text}")

    TOKEN = resp.json()["access_token"]
    log.info("API login successful")


def auth_headers():
    return {"Authorization": f"Bearer {TOKEN}"}


def safe_request(method, url, **kwargs):
    global TOKEN

    resp = requests.request(method, url,**kwargs)

    if resp.status_code == 401:
        api_login()
        kwargs["headers"] = auth_headers()
        resp = requests.request(method, url , **kwargs)

    return resp


# =====================================================
# DB / FSM HELPERS
# =====================================================

def get_or_create_user(chat_id: int, username: str | None):
    db: Session = SessionLocal()
    try:
        user = db.get(TelegramUser, chat_id)
        if not user:
            user = TelegramUser(
                telegram_id=chat_id,
                username=username,
                state="IDLE",
                questions = None,
                answers = None,
                request_id = None
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    finally:
        db.close()


def update_user(chat_id: int, **fields):
    db: Session = SessionLocal()
    try:
        user = db.get(TelegramUser, chat_id)
        if not user:
            return
        for key, value in fields.items():
            setattr(user, key, value)
        db.commit()
    finally:
        db.close()


def save_game_session(chat_id, questions, answers, result):
            db = SessionLocal()
            try:
                session = GameSession(
                    telegram_id=chat_id,
                    questions=questions,
                    answers=answers,
                    result=result
                )
                db.add(session)
                db.commit()
            finally:
                db.close()



def export_game_sessions_to_file():
    israel_tz = ZoneInfo("Asia/Jerusalem")
    db = SessionLocal()
    try:
        sessions = db.query(GameSession).all()
        data = [
            {
                "id": s.id,
                "telegram_id": s.telegram_id,
                "questions": s.questions,
                "answers": s.answers,
                "result": s.result,
                "created_at": s.created_at.astimezone(israel_tz).isoformat(),
            }
            for s in sessions
        ]

        with open("/data/game_sessions.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    finally:
        db.close()


# =====================================================
# BOT COMMANDS
# =====================================================

@bot.message_handler(commands=["start"])
def start(message):
    api_login()
    time.sleep(5)
    get_or_create_user(
        message.chat.id,
        message.from_user.username
    )

    update_user(
        message.chat.id,
        state="IDLE",
        request_id=None,
        questions=None,
        answers = None,
    )

    bot.send_message(
        message.chat.id,
        "Welcome.\nUse /ask_question to start a trivia round."
    )


@bot.message_handler(commands=["ask_question"])
def ask_question(message):
    chat_id = message.chat.id
    parts = message.text.split(maxsplit=1)
    update_user(
        chat_id,
        state="AWAITING_TOPIC",
        request_id=None,
        questions=None,
        answers = None,
    )
    time.sleep(3)
    if len(parts) > 1:
        message.text = parts[1]
        handle_text(message)
    else:
        bot.send_message(chat_id, "Enter a trivia topic:")
        return

# =====================================================
# TEXT HANDLER (FSM)
# =====================================================

@bot.message_handler(content_types=["text"])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text.strip()

    user = get_or_create_user(chat_id, message.from_user.username)
    state = user.state

    # ---------------------------------------------
    # AWAITING_TOPIC
    # ---------------------------------------------
    if state == "AWAITING_TOPIC":
        resp = safe_request(
            "POST",
            f"{API_BASE}/requests/request", 
            json={
                "text": f"Provide four trivia questions about {text}, but don't mention the answers"
            },
            headers=auth_headers(),
        )

        if resp.status_code != 200:
            bot.send_message(chat_id, "Server error.")
            return

        request_id = resp.json()["request_id"]

        update_user(
            chat_id,
            state="WAITING_QUESTIONS",
            request_id=request_id
        )

        bot.send_message(chat_id, "Generating questions… Send any message to check status.")
        return

    # ---------------------------------------------
    # WAITING_QUESTIONS
    # ---------------------------------------------
    if state == "WAITING_QUESTIONS":
        if not user.request_id:
            bot.send_message(chat_id, "Session expired. Use /ask_question.")
            return
        resp = safe_request(
            "GET",
            f"{API_BASE}/requests/result/{user.request_id}",
            headers=auth_headers(),
        )

        if resp.status_code != 200:
            bot.send_message(chat_id, "still working ")
            return

        data = resp.json()

        if data["status"] != "done":
            bot.send_message(chat_id, "Still working…")
            return

        questions = data["result"]

        update_user(
            chat_id,
            state="AWAITING_ANSWERS",
            request_id = None,
            questions=questions
        )

        bot.send_message(chat_id, questions)
        bot.send_message(chat_id, "Write your answers:")
        return

    # ---------------------------------------------
    # AWAITING_ANSWERS
    # ---------------------------------------------
    if state == "AWAITING_ANSWERS":
        answers = text
        resp = safe_request(
            "POST",
            f"{API_BASE}/requests/request",
            json={
                "text": (
                    f"Check these answers: {answers}. "
                    f"Based on these questions: {user.questions}. "
                    "If correct say correct, if incorrect provide correct answer "
                )
            },
            headers=auth_headers(),
        )

        if resp.status_code != 200:
            bot.send_message(chat_id, "Server error.")
            return

        request_id = resp.json()["request_id"]

        update_user(
            chat_id,
            state="WAITING_EVALUATION",
            request_id=request_id,
            answers = answers
        )

        bot.send_message(chat_id, "Evaluating answers… Send any message to check status.")
        return

    # ---------------------------------------------
    # WAITING_EVALUATION
    # ---------------------------------------------
    if state == "WAITING_EVALUATION":
        if not user.request_id:
            bot.send_message(chat_id, " session finished Reply  yes or no. to continue ")
            return
        
        resp = safe_request(
            "GET",
            f"{API_BASE}/requests/result/{user.request_id}",
            headers=auth_headers(),
        )
       
        if resp.status_code != 200:
            bot.send_message(chat_id, "still working")
            return

        data = resp.json()

        if data["status"] != "done":
            bot.send_message(chat_id, "Still working…")
            return

        bot.send_message(chat_id, data["result"])
        save_game_session(
            chat_id,
            questions= user.questions,
            answers=user.answers,
            result=data["result"]
            )  
    
        update_user(
            chat_id,
            state="AWAITING_RESTART",
            request_id=None   # <-- קריטי
        )
        bot.send_message(chat_id, "Do you want to play again? (yes / no)")
        return
    # ---------------------------------------------
    # AWAITING_RESTART
    # ---------------------------------------------
    if state == "AWAITING_RESTART":
        if text.lower() in ("yes", "y", "כן"):
            update_user(
                chat_id,
                state="AWAITING_TOPIC",
                request_id=None,
                questions=None,
                answers = None
            )
            bot.send_message(chat_id, "Great! Enter a new topic:")
        else:
            update_user(
                chat_id,
                state="IDLE",
                request_id=None,
                questions=None,
                answers = None,
            )
            bot.send_message(chat_id, "Thanks for playing! 🎉")
            export_game_sessions_to_file()
            time.sleep(5)
            SCRIPT_PATH = "/folder_for_lambda/lambda_saving_files.py"
            print("SCRIPT_PATH = " , SCRIPT_PATH)
            print("EXIST = " , os.path.exists(SCRIPT_PATH))
            subprocess.run ( ["python" , SCRIPT_PATH] , 
                            check = True,   
                            env=os.environ 
                           )
            time.sleep(5)
            GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN" , "")
            SCRIPT_PATH = "/folder_for_git_scripts/git_push.sh"
            print("SCRIPT_PATH =", SCRIPT_PATH)
            print("EXISTS =", os.path.exists(SCRIPT_PATH))
            subprocess.run(
            ["bash", SCRIPT_PATH],
            check= True,
            env={**os.environ, "GITHUB_TOKEN": GITHUB_TOKEN}  
            ) #**os.environ -> copy all existing environment variables from system 
              # and by : "GITHUB_TOKEN": GITHUB_TOKEN -> we update the existing environment variable




if __name__ == "__main__":
    bot.polling(none_stop=True)

