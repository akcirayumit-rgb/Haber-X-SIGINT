#!/usr/bin/env python3
"""GPS Navigation & Satellite Data Monitor"""
import json, sys, time, random
from datetime import datetime

try:
    print("[gps-nav] Başlatıldı", file=sys.stderr, flush=True)
    iteration = 0
    while True:
        print(json.dumps({
            "type": "gps-nav",
            "latitude": round(random.uniform(-90, 90), 6),
            "longitude": round(random.uniform(-180, 180), 6),
            "altitude_m": round(random.uniform(0, 3000), 1),
            "satellites_locked": random.randint(4, 12),
            "satellites_total": random.randint(12, 24),
            "snr_db": round(random.uniform(20, 45), 1),
            "hdop": round(random.uniform(0.8, 2.5), 2),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), flush=True)
        iteration += 1
        if iteration % 6 == 0:
            print(f"[gps-nav] {iteration} konum güncellendi", file=sys.stderr, flush=True)
        time.sleep(1)
except KeyboardInterrupt:
    print("[gps-nav] Durduruldu", file=sys.stderr, flush=True)
    sys.exit(0)
