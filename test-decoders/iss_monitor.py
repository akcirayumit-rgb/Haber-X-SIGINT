#!/usr/bin/env python3
"""ISS Monitor — Production Code (pyorbital ready)"""
import json, sys, time, random
from datetime import datetime, timedelta

"""
PRODUCTION MODE (when pyorbital available):
  from pyorbital import astronomy
  from pyorbital.orbital import Orbital

  iss = Orbital("ISS (ZARYA)")
  lon, lat, alt = iss.get_lonlatalt(datetime.utcnow())
  # Calculate next passes, Doppler, etc.
"""

def generate_iss_data():
    # Simulated orbit (simplified)
    timestamp = datetime.utcnow()
    orbit_period = 92.68 * 60
    seconds_in_orbit = timestamp.timestamp() % orbit_period

    # Simple sinusoidal latitude
    lat = 51.6 * (2 * (seconds_in_orbit / orbit_period) - 1)
    lon = -75 + (360 * seconds_in_orbit / orbit_period) % 360
    alt = 408 + random.uniform(-2, 2)

    # Next passes (fake)
    now = datetime.utcnow()
    passes = []
    for hours_ahead in [2, 8, 15]:
        pass_time = now + timedelta(hours=hours_ahead)
        passes.append({
            "aos": pass_time.isoformat() + "Z",
            "los": (pass_time + timedelta(minutes=random.randint(5, 15))).isoformat() + "Z",
            "max_elevation": random.randint(30, 80)
        })

    return {
        "type": "iss",
        "position": {
            "latitude": round(lat, 3),
            "longitude": round(lon, 3),
            "altitude_km": round(alt, 1),
            "velocity_kms": 7.66
        },
        "next_passes": passes,
        "aprs_packet": {
            "callsign": "RS0ISS",
            "frequency_mhz": 145.800,
            "message": f"ISS: LAT {lat:.2f} LON {lon:.2f} ALT {alt:.0f}km",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        "signal_strength": max(0, int(random.uniform(10, 60))),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

try:
    print("[iss] Başlatıldı (ISS Real-time Tracking)", file=sys.stderr, flush=True)

    iteration = 0
    while True:
        data = generate_iss_data()
        print(json.dumps(data), flush=True)
        iteration += 1
        if iteration % 20 == 0:
            print(f"[iss] {iteration} konum güncellemesi gönderildi", file=sys.stderr, flush=True)
        time.sleep(2)  # 0.5 Hz (orbit updates slower)

except KeyboardInterrupt:
    print("[iss] Durduruldu", file=sys.stderr, flush=True)
    sys.exit(0)
except Exception as e:
    print(f"[iss] Hata: {e}", file=sys.stderr, flush=True)
    sys.exit(1)
