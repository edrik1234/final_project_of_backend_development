import requests
import bot.app.config as config

def generate_questions(topic):
    try:
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.DEEPSEEK_KEY}"
        }

        prompt = (
            f"Create four trivia questions about the topic: {topic}.\n"
            f"After the user answers all of them or if he don't knows, provide: \n"
            f"1. The correct answers\n"
            f"2. The final grade\n"
            f"3. Ask if he wants to play again."
        )

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that provides clear, accurate, and useful responses to user questions and requests."},
                {"role": "user", "content": prompt}
            ]
        }

        r = requests.post(url, json=payload, headers=headers)
        answer = r.json()["choices"][0]["message"]["content"]
        return answer

    except Exception as e:
        return f"Error: {str(e)}"





def user_request(topic, message):
    try:
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.DEEPSEEK_KEY}"
        }

        prompt = (
           f"{message} -> give an answers questions you asked about  {topic} and ask if the user wants a new game"
        )

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that provides clear, accurate, and useful responses to user questions and requests."},
                {"role": "user", "content": prompt}
            ]
        }

        r = requests.post(url, json=payload, headers=headers)
        answer = r.json()["choices"][0]["message"]["content"]
        return answer

    except Exception as e:
        return f"Error: {str(e)}"
