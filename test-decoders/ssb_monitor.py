#!/usr/bin/env python3
"""SSB/LSB Voice Decoder"""
import json, sys, time, random
from datetime import datetime

CALLSIGNS = ["W5XYZ", "N0CALL", "K4ABC", "VE3XYZ", "G3RZP"]
MESSAGES = ["CQ CQ CQ", "ROGER", "WILCO", "BREAK BREAK", "QTH?"]

try:
    args = sys.argv[1:]
    mode = "LSB"
    for i, arg in enumerate(args):
        if arg == '--mode' and i + 1 < len(args):
            mode = args[i + 1].upper()

    print(f"[ssb] Başlatıldı ({mode})", file=sys.stderr, flush=True)
    iteration = 0
    while True:
        print(json.dumps({
            "type": "ssb",
            "frequency_mhz": 7.040,
            "mode": mode,
            "callsign": random.choice(CALLSIGNS),
            "message": random.choice(MESSAGES),
            "snr_db": round(random.uniform(5, 25), 1),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), flush=True)
        iteration += 1
        if iteration % 6 == 0:
            print(f"[ssb] {iteration} sinyal çözüldü", file=sys.stderr, flush=True)
        time.sleep(1.2)
except KeyboardInterrupt:
    print("[ssb] Durduruldu", file=sys.stderr, flush=True)
    sys.exit(0)
