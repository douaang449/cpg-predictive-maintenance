import json
import time
import argparse
import pandas as pd
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC_TEMPLATE = "cpg/equipment/{machine_id}/telemetry"


TYPE_TO_MACHINE_ID = {
    "L": 2,
    "M": 3,
    "H": 4,
}


def run(csv_path: str, speed: float = 5.0, broker: str = BROKER, port: int = PORT):
    df = pd.read_csv(csv_path)
    client = mqtt.Client()
    client.connect(broker, port, 60)
    client.loop_start()

    print(f"Streaming {len(df)} readings to {broker}:{port} (speed x{speed} readings/sec)...")

    for _, row in df.iterrows():
        equipment_class = row["Type"]
        machine_id = TYPE_TO_MACHINE_ID.get(equipment_class)
        if machine_id is None:
            continue  # skip rows for unmapped classes

        payload = {
            "machine_id": machine_id,
            "ambient_temp_k": row["Air temperature [K]"],
            "motor_temp_k": row["Process temperature [K]"],
            "shaft_rpm": row["Rotational speed [rpm]"],
            "load_torque_nm": row["Torque [Nm]"],
            "operating_minutes": row["Tool wear [min]"],
        }

        topic = TOPIC_TEMPLATE.format(machine_id=machine_id)
        client.publish(topic, json.dumps(payload))
        print(f"Published -> {topic}: temp={payload['motor_temp_k']}K")
        time.sleep(1.0 / speed)

    client.loop_stop()
    client.disconnect()
    print("Stream finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="data/ai4i2020.csv")
    parser.add_argument("--speed", type=float, default=5.0, help="readings per second")
    args = parser.parse_args()
    run(args.csv, args.speed)