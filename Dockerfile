FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5178

ENV FLASK_ENV=production

CMD ["python", "server.py"]