FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/src

EXPOSE 9091

CMD ["python", "-m", "uvicorn", "blog_chat.main:app", "--host", "0.0.0.0", "--port", "9091"]
