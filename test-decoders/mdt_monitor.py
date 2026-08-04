#!/usr/bin/env python3
"""Taxi MDT Signal Decoder"""
import json, sys, time, random
from datetime import datetime

UNITS = ["42", "15", "87", "23", "56"]
STATUSES = ["AVAILABLE", "ASSIGNED", "EN ROUTE", "AT SCENE", "RETURNING"]

try:
    print("[mdt] Başlatıldı", file=sys.stderr, flush=True)
    iteration = 0
    while True:
        print(json.dumps({
            "type": "mdt",
            "frequency_mhz": 406.625,
            "unit": random.choice(UNITS),
            "call_number": f"{random.randint(1000, 9999)}",
            "status": random.choice(STATUSES),
            "message": f"UNIT {random.choice(UNITS)} ASSIGNED CALL {random.randint(1000, 9999)}",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), flush=True)
        iteration += 1
        if iteration % 8 == 0:
            print(f"[mdt] {iteration} paket çözüldü", file=sys.stderr, flush=True)
        time.sleep(0.8)
except KeyboardInterrupt:
    print("[mdt] Durduruldu", file=sys.stderr, flush=True)
    sys.exit(0)
