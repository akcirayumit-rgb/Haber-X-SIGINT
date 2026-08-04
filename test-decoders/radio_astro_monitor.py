#!/usr/bin/env python3
"""Radio Astronomy Monitor (1.4 GHz H-line)"""
import json, sys, time, random
from datetime import datetime

SOURCES = ["Cassiopeia A", "Cygnus A", "Orion Nebula", "Virgo A", "Sagittarius A*"]

try:
    print("[astro] Başlatıldı", file=sys.stderr, flush=True)
    iteration = 0
    while True:
        print(json.dumps({
            "type": "radio-astro",
            "source": random.choice(SOURCES),
            "ra": f"{random.randint(0,23):02d}h{random.randint(0,59):02d}m",
            "dec": f"{random.randint(-90,90):+03d}°",
            "frequency_mhz": 1420.405,
            "flux_density_jy": round(random.uniform(1, 100), 2),
            "snr_db": round(random.uniform(5, 40), 1),
            "integration_time_s": random.randint(10, 300),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), flush=True)
        iteration += 1
        if iteration % 4 == 0:
            print(f"[astro] {iteration} gözlem tamamlandı", file=sys.stderr, flush=True)
        time.sleep(2)
except KeyboardInterrupt:
    print("[astro] Durduruldu", file=sys.stderr, flush=True)
    sys.exit(0)
