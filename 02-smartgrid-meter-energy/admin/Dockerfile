FROM python:3.9-slim
WORKDIR /srv/admin
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY meter_admin ./meter_admin
COPY run.py .
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["python", "run.py"]
