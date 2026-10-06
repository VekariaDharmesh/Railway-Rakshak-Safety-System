import time
import json
import random
import requests
from datetime import datetime

API_URL = "http://127.0.0.1:8000/api/v1/sensor-data"

SENSORS = {
    # North
    "DEL_UMB_001_ACC": {"lat": 28.6139, "lng": 77.2090}, # Delhi
    "DEL_UMB_002_ACC": {"lat": 29.3909, "lng": 76.9635}, # Panipat
    "CHD_ASR_001_ACC": {"lat": 30.7333, "lng": 76.7794}, # Chandigarh
    "JAI_AJE_001_ACC": {"lat": 26.9124, "lng": 75.7873}, # Jaipur
    # West
    "MUM_PUN_001_ACC": {"lat": 19.0760, "lng": 72.8777}, # Mumbai
    "MUM_PUN_002_ACC": {"lat": 18.5204, "lng": 73.8567}, # Pune
    "AMD_BRC_001_ACC": {"lat": 23.0225, "lng": 72.5714}, # Ahmedabad
    "SRT_BRC_001_ACC": {"lat": 21.1702, "lng": 72.8311}, # Surat
    # South
    "BLR_MYS_001_ACC": {"lat": 12.9716, "lng": 77.5946}, # Bangalore
    "MAA_MDU_001_ACC": {"lat": 13.0827, "lng": 80.2707}, # Chennai
    "HYD_VJA_001_ACC": {"lat": 17.3850, "lng": 78.4867}, # Hyderabad
    "COK_TRV_001_ACC": {"lat": 9.9312, "lng": 76.2673},  # Kochi
    # East
    "CCU_BBS_001_ACC": {"lat": 22.5726, "lng": 88.3639}, # Kolkata
    "BBS_VSK_001_ACC": {"lat": 20.2961, "lng": 85.8245}, # Bhubaneswar
    "PNQ_NAG_001_ACC": {"lat": 21.1458, "lng": 79.0882}, # Nagpur
    # Central
    "BPL_IND_001_ACC": {"lat": 23.2599, "lng": 77.4126}, # Bhopal
    "LKO_CNB_001_ACC": {"lat": 26.8467, "lng": 80.9462}, # Lucknow
    "PAT_GAY_001_ACC": {"lat": 25.5941, "lng": 85.1376}, # Patna
    # Additional 7 locations to reach 25
    "GHY_DBR_001_ACC": {"lat": 26.1445, "lng": 91.7362}, # Guwahati
    "VAR_DDU_001_ACC": {"lat": 25.3176, "lng": 82.9739}, # Varanasi
    "AGR_GWL_001_ACC": {"lat": 27.1767, "lng": 78.0081}, # Agra
    "JBP_KAT_001_ACC": {"lat": 23.1815, "lng": 79.9864}, # Jabalpur
    "CBE_ED_001_ACC": {"lat": 11.0168, "lng": 76.9558}, # Coimbatore
    "VSK_BZA_001_ACC": {"lat": 17.6868, "lng": 83.2185}, # Visakhapatnam
    "DND_KGP_001_ACC": {"lat": 23.7947, "lng": 86.4304}, # Dhanbad
}

def generate_normal_data():
    return {
        "peak_freq": random.uniform(200, 300),
        "rms_accel": random.uniform(0.1, 0.5),
        "crest_factor": random.uniform(2.0, 3.5),
        "band1": random.uniform(0.05, 0.15),
        "band2": random.uniform(0.05, 0.15),
        "band3": random.uniform(0.05, 0.15),
        "acoustic_peak": random.uniform(0.5, 1.5),
        "acoustic_rms": random.uniform(0.2, 0.8),
        "temp": random.uniform(20.0, 26.0),
        "weather_condition": random.choice(["Clear", "Partly Cloudy"]),
        "humidity": random.uniform(40.0, 60.0)
    }

def generate_anomaly_data():
    return {
        "peak_freq": random.uniform(1000, 1500), # High freq resonance
        "rms_accel": random.uniform(2.0, 4.0),   # High vibration
        "crest_factor": random.uniform(6.0, 10.0), # Impulsive
        "band1": random.uniform(0.01, 0.05),
        "band2": random.uniform(0.4, 0.8),       # Power shifted
        "band3": random.uniform(0.1, 0.3),
        "acoustic_peak": random.uniform(8.0, 15.0), # Stress clicks
        "acoustic_rms": random.uniform(4.0, 8.0),
        "temp": random.uniform(28.0, 35.0),       # Elevated temp
        "weather_condition": random.choice(["Heavy Rain", "Thunderstorm"]),
        "humidity": random.uniform(80.0, 100.0)
    }

def simulate():
    print("Starting Rail Sensor Simulator...")
    
    # Send some initial normal data to establish baseline
    for _ in range(3):
        for sensor, coords in SENSORS.items():
            data = {
                "sensor_id": sensor,
                "timestamp": time.time(),
                "values": generate_normal_data(),
                "health": "OK",
                "location": coords
            }
            try:
                requests.post(API_URL, json=data)
            except requests.exceptions.ConnectionError:
                print(f"Warning: Backend not reachable at {API_URL}")
        time.sleep(1)

    # Main loop
    while True:
        # Determine if we should generate an anomaly (10% chance)
        is_anomaly = random.random() < 0.1
        anomalous_sensor = random.choice(list(SENSORS.keys())) if is_anomaly else None
        
        for sensor, coords in SENSORS.items():
            if sensor == anomalous_sensor:
                print(f"Triggering ANOMALY on {sensor}")
                values = generate_anomaly_data()
            else:
                values = generate_normal_data()
                
            data = {
                "sensor_id": sensor,
                "timestamp": time.time(),
                "values": values,
                "health": "OK",
                "location": coords
            }
            
            try:
                requests.post(API_URL, json=data)
            except requests.exceptions.ConnectionError:
                print("Failed to connect to backend...")
                time.sleep(5)
                break

        # Occasionally generate a cyber-physical threat or system update
        if is_anomaly and anomalous_sensor:
            try:
                threat_payload = {
                    "severity": random.choice(["HIGH", "MEDIUM"]),
                    "location": f"{anomalous_sensor} (Corridor KM {random.randint(120, 680)})",
                    "event": random.choice([
                        "Acoustic frequency harmonic spike (stress defect)",
                        "Impulsive vibration acceleration deviation (joint shear)",
                        "Excessive thermal gradient detected on rail head"
                    ]),
                    "category": "PHYSICAL_DEFECT"
                }
                requests.post("http://127.0.0.1:8000/api/v1/threats", json=threat_payload)

                event_payload = {
                    "category": "OPERATION",
                    "source": "SIMULATOR",
                    "description": f"Automated inspection triggered for {anomalous_sensor}",
                    "status": "ACTIVE",
                    "tab": "live"
                }
                requests.post("http://127.0.0.1:8000/api/v1/events", json=event_payload)
            except Exception as e:
                pass
                
        print(f"Sent update at {datetime.now().isoformat()}")
        time.sleep(5) # Send data every 5 seconds

if __name__ == "__main__":
    time.sleep(2) # Give API time to start
    simulate()
