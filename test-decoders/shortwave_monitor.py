#!/usr/bin/env python3
"""Shortwave Monitor — Production Code (test harness ready)"""
import json, sys, time, random
from datetime import datetime

BROADCASTERS = [
    {"freq": 6.090, "name": "DRM Broadcast", "lang": "Multi", "region": "Europe", "text": "Digital radio broadcast"},
    {"freq": 7.285, "name": "Voice of America", "lang": "English", "region": "Europe", "text": "News from Washington"},
    {"freq": 9.405, "name": "DW Deutsche Welle", "lang": "German", "region": "Africa", "text": "Nachrichten aus Berlin"},
    {"freq": 11.580, "name": "BBC World Service", "lang": "English", "region": "Asia", "text": "This is BBC World Service"},
    {"freq": 15.575, "name": "Radio Pakistan", "lang": "Urdu", "region": "South Asia", "text": "پاکستان سے آپ کا خیرمقدم"},
    {"freq": 17.850, "name": "Voice of America", "lang": "English", "region": "Africa", "text": "VoA Special English"},
]

def generate_shortwave_data(target_freq):
    broadcaster = min(BROADCASTERS, key=lambda b: abs(b['freq'] - target_freq))
    snr = 15 - (abs(broadcaster['freq'] - target_freq) * 8)
    snr = max(5, snr + random.uniform(-2, 2))

    return {
        "type": "shortwave",
        "frequency_mhz": round(target_freq, 3),
        "broadcaster": broadcaster["name"],
        "language": broadcaster["lang"],
        "region": broadcaster["region"],
        "radio_text": broadcaster["text"],
        "snr_db": round(snr, 1),
        "signal_strength": max(0, min(100, int((snr + 30) * 2))),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

try:
    args = sys.argv[1:]
    target_freq = 9.405
    for i, arg in enumerate(args):
        if arg == '--freq' and i + 1 < len(args):
            target_freq = float(args[i + 1])

    print(f"[shortwave] Başlatıldı: {target_freq} MHz", file=sys.stderr, flush=True)

    iteration = 0
    while True:
        data = generate_shortwave_data(target_freq)
        print(json.dumps(data), flush=True)
        iteration += 1
        if iteration % 10 == 0:
            print(f"[shortwave] {iteration} paket gönderildi", file=sys.stderr, flush=True)
        time.sleep(1)

except KeyboardInterrupt:
    print("[shortwave] Durduruldu", file=sys.stderr, flush=True)
    sys.exit(0)
except Exception as e:
    print(f"[shortwave] Hata: {e}", file=sys.stderr, flush=True)
    sys.exit(1)
