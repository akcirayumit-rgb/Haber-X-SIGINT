#!/usr/bin/env python3
"""NOAA / Meteor-M Satellite Monitor"""
import json, sys, time, random
from datetime import datetime

SATELLITES = ["NOAA-18", "NOAA-19", "Meteor-M2", "Meteor-M2-2"]
CHANNELS = ["VIS", "IR", "WV"]
AREAS = ["Atlantic", "Pacific", "Indian Ocean", "Arctic", "Antarctic"]

try:
    print("[noaa] Başlatıldı", file=sys.stderr, flush=True)
    iteration = 0
    while True:
        print(json.dumps({
            "type": "noaa",
            "satellite": random.choice(SATELLITES),
            "frequency_mhz": [137.62, 137.91, 190.4][random.randint(0, 2)],
            "elevation_deg": round(random.uniform(5, 80), 1),
            "channel": random.choice(CHANNELS),
            "coverage_area": random.choice(AREAS),
            "lines_decoded": random.randint(100, 2500),
            "signal_quality_percent": random.randint(70, 100),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), flush=True)
        iteration += 1
        if iteration % 5 == 0:
            print(f"[noaa] {iteration} görüntü işlendi", file=sys.stderr, flush=True)
        time.sleep(2)
except KeyboardInterrupt:
    print("[noaa] Durduruldu", file=sys.stderr, flush=True)
    sys.exit(0)
