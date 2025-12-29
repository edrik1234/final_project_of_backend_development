FROM python:3.11-slim
RUN apt-get update && \
    apt-get install -y git openssh-client && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app/bot
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/bot"
COPY bot/app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY api_server_edrian/. /app/api_server_edrian/
COPY bot/app/. /app/bot/app
COPY shared_edrian/. /app/shared_edrian/
COPY logic_worker_edrian/. /app/logic_worker_edrian/
COPY folder_for_git_scripts/ /folder_for_git_scripts/
COPY folder_for_lambda/ /folder_for_lambda/
RUN chmod +x /folder_for_git_scripts/git_push.sh
CMD ["python","-m", "bot.app.telegram_bot"]
