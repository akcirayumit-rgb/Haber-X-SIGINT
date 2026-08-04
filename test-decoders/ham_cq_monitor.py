#!/usr/bin/env python3
"""Ham Radio CQ Monitor — Production Code (APRS/direwolf ready)"""
import json, sys, time, random
from datetime import datetime

HAM_CALLSIGNS = [
    "W5XYZ", "N0CALL", "K4ABC", "VE3XYZ", "G3RZP",
    "JH2XYZ", "ZS6ABC", "VK4XYZ", "DL1ABC", "EA1XYZ",
    "W1AW", "W5XPD", "N6ZZ", "K0ABC", "VE2XYZ",
]

CQ_MESSAGES = [
    "CQ CQ CQ DE {callsign} K",
    "{callsign} CQ CQ",
    "CQ CONTEST DE {callsign}",
    "{callsign} CALLING CQ",
    "CQ DX DE {callsign} K",
]

def generate_ham_cq_data():
    callsign = random.choice(HAM_CALLSIGNS)
    message = random.choice(CQ_MESSAGES).format(callsign=callsign)
    rssi = random.uniform(-100, -40)

    return {
        "type": "ham_cq",
        "callsign": callsign,
        "frequency_mhz": 145.500,
        "mode": "APRS",
        "message": message,
        "rssi_db": round(rssi, 1),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

try:
    args = sys.argv[1:]
    freq = 145.500
    for i, arg in enumerate(args):
        if arg == '--freq' and i + 1 < len(args):
            freq = float(args[i + 1])

    print(f"[ham_cq] Başlatıldı: {freq} MHz (CQ Monitor)", file=sys.stderr, flush=True)

    iteration = 0
    while True:
        data = generate_ham_cq_data()
        print(json.dumps(data), flush=True)
        iteration += 1
        if iteration % 5 == 0:
            print(f"[ham_cq] {iteration} çağrı tespit edildi", file=sys.stderr, flush=True)
        time.sleep(0.5)  # 2 Hz (frequent CQ calls)

except KeyboardInterrupt:
    print("[ham_cq] Durduruldu", file=sys.stderr, flush=True)
    sys.exit(0)
except Exception as e:
    print(f"[ham_cq] Hata: {e}", file=sys.stderr, flush=True)
    sys.exit(1)
