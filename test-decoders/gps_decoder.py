#!/usr/bin/env python3
"""
GPS Decoder Test Harness
Fake GPS/GNSS position data
"""

import json
import sys
import time
import random
from datetime import datetime

def generate_gps_data():
    """Generate fake GPS position data"""
    # Istanbul region
    base_lat = 41.0082
    base_lon = 28.9784
    base_alt = 50

    # Random walk simulation
    lat = base_lat + random.uniform(-0.01, 0.01)
    lon = base_lon + random.uniform(-0.01, 0.01)
    alt = base_alt + random.uniform(-10, 50)

    # Variable satellite count (4-15 sats)
    num_sats = random.randint(4, 15)

    # Generate per-satellite SNR
    sats = []
    for i in range(num_sats):
        sats.append({
            "prn": i + 1,
            "snr_db": random.uniform(25, 45),
            "elevation": random.uniform(-10, 90),
            "azimuth": random.uniform(0, 360)
        })

    # Calculate DOP values (simplified)
    if num_sats >= 4:
        gdop = random.uniform(2, 8)
        pdop = gdop * 0.7
        hdop = pdop * 0.8
    else:
        gdop = hdop = pdop = 99.9

    return {
        "type": "gps",
        "position": {
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "altitude_m": round(alt, 1)
        },
        "velocity": {
            "heading_deg": random.uniform(0, 360),
            "speed_mps": random.uniform(0, 2),
            "vertical_speed": random.uniform(-0.5, 0.5)
        },
        "fix_quality": {
            "type": "3D" if num_sats >= 4 else "2D",
            "num_satellites": num_sats,
            "gdop": round(gdop, 2),
            "pdop": round(pdop, 2),
            "hdop": round(hdop, 2),
            "satellites": sats
        },
        "signal_strength": max(0, min(100, int(num_sats * 6))),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

def main():
    """Main loop"""
    try:
        print("[gps_decoder] Başlatıldı (test mode)", file=sys.stderr, flush=True)

        iteration = 0
        while True:
            data = generate_gps_data()
            print(json.dumps(data), flush=True)

            iteration += 1
            if iteration % 10 == 0:
                print(f"[gps_decoder] {iteration} pozisyon güncellemesi gönderildi", file=sys.stderr, flush=True)

            time.sleep(1)  # 1 Hz update rate

    except KeyboardInterrupt:
        print("[gps_decoder] Durduruldu", file=sys.stderr, flush=True)
        sys.exit(0)
    except Exception as e:
        print(f"[gps_decoder] Hata: {e}", file=sys.stderr, flush=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
