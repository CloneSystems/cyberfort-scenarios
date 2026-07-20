"""SmartGrid telemetry publisher.

Simulates three smart meters pushing readings to the MQTT broker every
five seconds. The publisher uses hard-coded MQTT credentials even
though the broker is currently configured for anonymous access.
"""

import json
import os
import random
import time

import paho.mqtt.client as mqtt

MQTT_HOST = os.environ.get("MQTT_HOST", "mqtt")
MQTT_PORT = 1883

# VULN-5: the deployment team hard-coded credentials in source code
# "for convenience". Even though the broker now accepts anonymous
# connections, these credentials still live in the repo.
MQTT_USER = "ops"
MQTT_PASSWORD = "OpsTopSecret#2024"


def main():
    client = mqtt.Client(client_id="telemetry-publisher")
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    for _ in range(20):
        try:
            client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
            break
        except Exception:
            time.sleep(2)
    else:
        print("could not reach mqtt broker, giving up")
        return

    meters = ["meter-larnaca-001", "meter-paphos-014", "meter-nicosia-027"]
    while True:
        for m in meters:
            payload = {
                "meter_id": m,
                "ts": int(time.time()),
                "power_w": random.randint(2800, 5800),
                "voltage_v": round(229 + random.random() * 2, 2),
                "kwh": round(random.uniform(120, 140) * 1000, 1),
                "tariff": random.choice(["day", "night"]),
            }
            client.publish(f"smartgrid/{m}/telemetry", json.dumps(payload))
        time.sleep(5)


if __name__ == "__main__":
    main()
