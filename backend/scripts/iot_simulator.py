import time
import json
import random
import requests
from datetime import datetime
import os

API_URL = "http://localhost:8000/api/v1/vitals/1/stream"

def generate_vitals(induce_anomaly=False):
    if induce_anomaly:
        return {
            "heart_rate": random.randint(105, 130),
            "spo2": random.randint(85, 91),
            "temperature_c": round(random.uniform(38.0, 39.5), 1),
            "timestamp": datetime.now().isoformat()
        }
    return {
        "heart_rate": random.randint(60, 90),
        "spo2": random.randint(95, 100),
        "temperature_c": round(random.uniform(36.5, 37.2), 1),
        "timestamp": datetime.now().isoformat()
    }

def main():
    print("Starting Wearable IoT Telemetry Simulator...")
    print(f"Targeting Patient ID 1 at {API_URL}")
    print("Press Ctrl+C to stop.\n")
    
    counter = 0
    try:
        while True:
            # 1 in 10 chance to simulate a sudden deterioration
            induce_anomaly = random.randint(1, 10) == 1
            payload = generate_vitals(induce_anomaly)
            
            try:
                response = requests.post(API_URL, json=payload, timeout=5)
                # Ignore connection errors silently to not spam if server is off
                if response.status_code == 200:
                    result = response.json()
                    
                    log = f"Sent Vitals -> HR: {payload['heart_rate']} | SpO2: {payload['spo2']}% | Temp: {payload['temperature_c']}C"
                    if result.get("anomalies_detected"):
                        print(f"\033[91m[ALERT TRIGGERED] {log}\033[0m")
                    else:
                        print(f"[OK] {log}")
            except requests.exceptions.RequestException:
                print("Failed to connect to backend API... retrying in 2 seconds.")
                
            time.sleep(2)
            counter += 1
    except KeyboardInterrupt:
        print("\nSimulator stopped.")

if __name__ == "__main__":
    main()
