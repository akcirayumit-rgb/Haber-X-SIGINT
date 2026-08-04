#!/usr/bin/env python3
"""OTH Radar / HAARP Detection Monitor"""
import json, sys, time, random
from datetime import datetime

MODES = ["OTH Radar", "HAARP", "Duga"]
TARGETS = ["Russia", "China", "Maritime", "Atmospheric", "Unknown"]

try:
    print("[oth] Başlatıldı", file=sys.stderr, flush=True)
    iteration = 0
    while True:
        print(json.dumps({
            "type": "oth",
            "mode": random.choice(MODES),
            "frequency_mhz": round(random.uniform(5, 30), 2),
            "beam_map_sector": f"{random.randint(0, 360)}°",
            "beam_direction_azimuth": random.randint(0, 360),
            "beam_elevation_angle": round(random.uniform(10, 30), 1),
            "pulse_repetition_rate_hz": random.randint(5, 100),
            "pulse_width_us": random.randint(100, 1000),
            "target_area": random.choice(TARGETS),
            "signal_strength_db": round(random.uniform(30, 80), 1),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), flush=True)
        iteration += 1
        if iteration % 10 == 0:
            print(f"[oth] {iteration} tarama tamamlandı", file=sys.stderr, flush=True)
        time.sleep(1.5)
except KeyboardInterrupt:
    print("[oth] Durduruldu", file=sys.stderr, flush=True)
    sys.exit(0)
