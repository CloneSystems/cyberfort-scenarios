FROM python:3.9-slim
WORKDIR /srv/modbus
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY simulator.py .
ENV PYTHONUNBUFFERED=1
EXPOSE 5020
CMD ["python", "simulator.py"]
