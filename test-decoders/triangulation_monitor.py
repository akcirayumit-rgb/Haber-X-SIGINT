#!/usr/bin/env python3
"""Triangulation / Direction Finding Monitor"""
import json, sys, time, random
from datetime import datetime

try:
    print("[triangulation] Başlatıldı", file=sys.stderr, flush=True)
    iteration = 0
    while True:
        lat = round(random.uniform(-90, 90), 4)
        lon = round(random.uniform(-180, 180), 4)
        print(json.dumps({
            "type": "triangulation",
            "estimated_latitude": lat,
            "estimated_longitude": lon,
            "bearing_1_deg": random.randint(0, 360),
            "bearing_2_deg": random.randint(0, 360),
            "bearing_3_deg": random.randint(0, 360),
            "error_radius_km": round(random.uniform(0.5, 50), 1),
            "confidence_percent": random.randint(60, 99),
            "signal_sources": random.randint(2, 5),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), flush=True)
        iteration += 1
        if iteration % 7 == 0:
            print(f"[triangulation] {iteration} konum çözümü", file=sys.stderr, flush=True)
        time.sleep(random.uniform(1, 3))
except KeyboardInterrupt:
    print("[triangulation] Durduruldu", file=sys.stderr, flush=True)
    sys.exit(0)
