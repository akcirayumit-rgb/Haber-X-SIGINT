#!/usr/bin/env python3
"""DAB+ Broadcast Decoder"""
import json, sys, time, random
from datetime import datetime

SERVICES = [
    {"name": "TRT 1", "bitrate": 128, "subchid": 0},
    {"name": "TRT FM", "bitrate": 96, "subchid": 1},
    {"name": "TRT Çocuk", "bitrate": 64, "subchid": 2},
    {"name": "NTV Radyo", "bitrate": 128, "subchid": 3},
]

try:
    print("[dab] Başlatıldı", file=sys.stderr, flush=True)
    iteration = 0
    while True:
        service = random.choice(SERVICES)
        print(json.dumps({
            "type": "dab",
            "ensemble": "TRT Ensemble",
            "service": service["name"],
            "bitrate": service["bitrate"],
            "subchid": service["subchid"],
            "text": f"Now: {service['name']} ({service['bitrate']} kbps)",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), flush=True)
        iteration += 1
        if iteration % 10 == 0:
            print(f"[dab] {iteration} paket gönderildi", file=sys.stderr, flush=True)
        time.sleep(1)
except KeyboardInterrupt:
    print("[dab] Durduruldu", file=sys.stderr, flush=True)
    sys.exit(0)
