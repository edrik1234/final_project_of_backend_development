FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/api_server_edrian"
WORKDIR /app/api_server_edrian
#essential build-tools for: bcrypt/passlib
#RUN apt-get update && \
   # apt-get install -y --no-install-recommends \
      #  build-essential \
       # libffi-dev \
       # python3-dev \
       # gcc \
       # g++ \
       # libssl-dev \
       # && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev python3-dev libssl-dev && \
    rm -rf /var/lib/apt/lists/*
COPY api_server_edrian/app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY shared_edrian/. /app/shared_edrian/
COPY api_server_edrian/. /app/api_server_edrian/
COPY bot/. /app/bot


EXPOSE 8000

CMD ["uvicorn", "api_server_edrian.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

