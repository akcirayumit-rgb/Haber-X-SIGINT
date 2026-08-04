#!/usr/bin/env python3
"""Digital Mode Decoder (CW/PSK/RTTY/SSTV)"""
import json, sys, time, random
from datetime import datetime

MODES = ["CW", "PSK31", "RTTY", "SSTV"]
TEXTS = {
    "CW": ".... . .-.. .-.. --- / .-- --- .-. .-..--",
    "PSK31": "CQ CQ CQ DE W5XYZ K",
    "RTTY": "RYRYRYRYRYRY",
    "SSTV": "SSTV IMAGE DATA"
}

try:
    args = sys.argv[1:]
    mode = "PSK31"
    for i, arg in enumerate(args):
        if arg == '--mode' and i + 1 < len(args):
            mode = args[i + 1].upper()

    print(f"[digital] Başlatıldı ({mode})", file=sys.stderr, flush=True)
    iteration = 0
    while True:
        print(json.dumps({
            "type": "digital",
            "frequency_mhz": 14.070,
            "mode": mode,
            "baudrate": [20, 31.25, 45, 73][MODES.index(mode) if mode in MODES else 1],
            "decoded_text": TEXTS.get(mode, "DATA"),
            "snr_db": round(random.uniform(3, 20), 1),
            "confidence": round(random.uniform(0.7, 0.99), 2),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), flush=True)
        iteration += 1
        if iteration % 7 == 0:
            print(f"[digital] {iteration} blok çözüldü", file=sys.stderr, flush=True)
        time.sleep(1.5)
except KeyboardInterrupt:
    print("[digital] Durduruldu", file=sys.stderr, flush=True)
    sys.exit(0)
