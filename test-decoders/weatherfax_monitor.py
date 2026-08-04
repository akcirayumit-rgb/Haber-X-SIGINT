#!/usr/bin/env python3
"""HF Weatherfax APT Decoder"""
import json, sys, time, random
from datetime import datetime

try:
    print("[weatherfax] Başlatıldı", file=sys.stderr, flush=True)
    iteration = 0
    while True:
        print(json.dumps({
            "type": "weatherfax",
            "satellite": ["NOAA-19", "NOAA-18"][random.randint(0, 1)],
            "frequency_mhz": [12.75, 14.40][random.randint(0, 1)],
            "image_type": ["VIS", "IR", "WV"][random.randint(0, 2)],
            "area": ["Atlantic", "Mediterranean", "Black Sea"][random.randint(0, 2)],
            "lines_received": random.randint(100, 320),
            "quality_percent": random.randint(60, 100),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), flush=True)
        iteration += 1
        if iteration % 5 == 0:
            print(f"[weatherfax] {iteration} frame alındı", file=sys.stderr, flush=True)
        time.sleep(2)
except KeyboardInterrupt:
    print("[weatherfax] Durduruldu", file=sys.stderr, flush=True)
    sys.exit(0)
