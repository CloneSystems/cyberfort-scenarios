FROM python:3.9-slim

WORKDIR /srv/portpilot

RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq5 \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY portpilot ./portpilot
COPY run.py .

ENV FLASK_APP=portpilot.app:app \
    PYTHONUNBUFFERED=1

EXPOSE 8080
CMD ["python", "run.py"]
