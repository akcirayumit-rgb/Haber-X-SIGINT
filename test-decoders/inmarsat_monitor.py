#!/usr/bin/env python3
"""Inmarsat GEO Satellite Communication Monitor"""
import json, sys, time, random
from datetime import datetime

SATELLITES = ["Inmarsat-4A F1", "Inmarsat-4A F2", "Inmarsat-4A F3", "Inmarsat-5 F1"]
BEAMS = ["Atlantic Ocean Region", "Indian Ocean Region", "Pacific Ocean Region"]

try:
    print("[inmarsat] Başlatıldı", file=sys.stderr, flush=True)
    iteration = 0
    while True:
        print(json.dumps({
            "type": "inmarsat",
            "satellite": random.choice(SATELLITES),
            "frequency_mhz": round(random.uniform(1535, 1545), 2),
            "beam_region": random.choice(BEAMS),
            "coverage_area": f"{random.randint(0,360)}° - {random.randint(0,360)}°",
            "signal_power_dbm": round(random.uniform(-100, -50), 1),
            "eirp": round(random.uniform(20, 50), 1),
            "traffic_load_percent": random.randint(10, 95),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), flush=True)
        iteration += 1
        if iteration % 6 == 0:
            print(f"[inmarsat] {iteration} uydu kontrol noktası", file=sys.stderr, flush=True)
        time.sleep(2)
except KeyboardInterrupt:
    print("[inmarsat] Durduruldu", file=sys.stderr, flush=True)
    sys.exit(0)
