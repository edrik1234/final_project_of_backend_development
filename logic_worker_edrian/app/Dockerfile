FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/logic_worker_edrian"
WORKDIR /app/logic_worker_edrian
COPY logic_worker_edrian/app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY shared_edrian/. /app/shared_edrian/
COPY logic_worker_edrian/. /app/logic_worker_edrian/

CMD ["python", "-m", "logic_worker_edrian.app.main"]




