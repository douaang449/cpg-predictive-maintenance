
import json
import paho.mqtt.client as mqtt

from app.core.database import SessionLocal
from app.core.models_registry import *  
from app.predictions.schemas import SensorReadingInput
from app.predictions.service import process_new_reading

BROKER = "localhost"
PORT = 1883
TOPIC = "cpg/equipment/+/telemetry"  


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connected to MQTT broker (code={reason_code})")
    client.subscribe(TOPIC)
    print(f"Subscribed to {TOPIC}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        reading = SensorReadingInput(**payload)
    except Exception as e:
        print(f"Malformed message on {msg.topic}: {e}")
        return

    db = SessionLocal()
    try:
        prediction = process_new_reading(db, reading)
        print(
            f"[{msg.topic}] machine={reading.machine_id} "
            f"proba={prediction.probabilite:.4f}"
        )
    except Exception as e:
        print(f"Error processing reading for machine {reading.machine_id}: {e}")
    finally:
        db.close()


def run():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    print("MQTT consumer running. ")
    client.loop_forever()


if __name__ == "__main__":
    run()