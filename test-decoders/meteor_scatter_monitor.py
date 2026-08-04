#!/usr/bin/env python3
"""Meteor Scatter Communication Monitor"""
import json, sys, time, random
from datetime import datetime

try:
    print("[meteor] Başlatıldı", file=sys.stderr, flush=True)
    iteration = 0
    while True:
        print(json.dumps({
            "type": "meteor",
            "frequency_mhz": 144.150,
            "meteor_trail_id": f"MTR-{random.randint(1000, 9999)}",
            "peak_magnitude": round(random.uniform(-2, 4), 1),
            "duration_ms": random.randint(100, 2000),
            "snr_db": round(random.uniform(5, 30), 1),
            "radiant_altitude_deg": round(random.uniform(20, 80), 1),
            "radiant_azimuth_deg": round(random.uniform(0, 360), 1),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), flush=True)
        iteration += 1
        if iteration % 8 == 0:
            print(f"[meteor] {iteration} meteor izi algılandı", file=sys.stderr, flush=True)
        time.sleep(random.uniform(0.5, 3))
except KeyboardInterrupt:
    print("[meteor] Durduruldu", file=sys.stderr, flush=True)
    sys.exit(0)
