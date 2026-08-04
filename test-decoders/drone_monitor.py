#!/usr/bin/env python3
"""Advanced Aircraft/Drone Tracking & Telemetry Monitor"""
import json, sys, time, random
from datetime import datetime

DRONE_MODELS = ["DJI Mavic 3", "DJI Air 3S", "DJI Mini 4 Pro", "Auterion Skynode", "AirDog SEVO"]
AIRCRAFT_MODELS = ["Boeing 737", "Airbus A320", "Cessna 172", "Piper Archer", "Unknown Aircraft"]
STATUSES = ["ARMED", "FLYING", "HOVERING", "LANDING", "IDLE", "IN_FLIGHT", "CLIMBING", "DESCENDING"]

try:
    print("[drone] Advanced Aircraft/Drone Radar başlatıldı", file=sys.stderr, flush=True)
    iteration = 0
    while True:
        # 70% drone, 20% aircraft, 10% belirsiz
        rand = random.random()

        if rand < 0.7:
            # DRONE
            obj_type = "drone"
            model = random.choice(DRONE_MODELS)
            freq = random.choice([900, 2400, 5800])
            heading = random.randint(0, 360)
            alt = random.randint(10, 500)
        elif rand < 0.9:
            # AIRCRAFT
            obj_type = "aircraft"
            model = random.choice(AIRCRAFT_MODELS)
            freq = random.choice([118, 121, 124, 127, 130, 1090])  # Aviation bands
            heading = random.randint(0, 360)
            alt = random.randint(500, 10000)
        else:
            # UNKNOWN
            obj_type = "unknown"
            model = f"Unknown-{random.randint(100, 999)}"
            freq = random.choice([869, 900, 915, 2400, 5800])
            heading = random.randint(0, 360)
            alt = random.randint(10, 5000)

        print(json.dumps({
            "type": "drone",
            "drone_id": f"{obj_type.upper()}-{random.randint(1000,9999)}",
            "model": model,
            "latitude": round(random.uniform(-90, 90), 6),
            "longitude": round(random.uniform(-180, 180), 6),
            "altitude_m": alt,
            "speed_ms": round(random.uniform(5, 50 if obj_type == "aircraft" else 20), 1),
            "heading_deg": heading,
            "battery_percent": random.randint(20, 100) if obj_type == "drone" else 100,
            "signal_strength_dbm": round(random.uniform(-95, -45), 1),
            "status": random.choice(STATUSES),
            "num_satellites": random.randint(8, 20),
            "frequency_mhz": freq,
            "object_type": obj_type,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), flush=True)

        iteration += 1
        if iteration % 10 == 0:
            print(f"[drone] {iteration} target tarandı", file=sys.stderr, flush=True)
        time.sleep(random.uniform(0.5, 2))
except KeyboardInterrupt:
    print("[drone] Durduruldu", file=sys.stderr, flush=True)
    sys.exit(0)
