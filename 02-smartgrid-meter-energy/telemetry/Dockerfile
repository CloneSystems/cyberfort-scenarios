FROM python:3.9-slim
WORKDIR /srv/telemetry
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY publisher.py .
ENV PYTHONUNBUFFERED=1
CMD ["python", "publisher.py"]
