#!/usr/bin/env python3
"""
Spectrum Analyzer — Production Code
Real-time FFT & waterfall display

PRODUCTION MODE (when SDR ready):
  - Spawns: rtl_power -f START:STOP:STEP -i 1 -g GAIN
  - Processes: CSV output → JSON FFT
  - Peak detection: Top N frequencies
  - Outputs: Waterfall rows, peak list, statistics

TEST MODE (current):
  - Generates realistic FM band spectrum
  - Simulates peak detection
  - Same JSON format (drop-in replacement)

MIGRATION: Uncomment line 30-60 when rtl_power available
"""

import json
import sys
import time
import random
import subprocess
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════
# PRODUCTION MODE: Real RTL-SDR (UNCOMMENT WHEN READY)
# ═══════════════════════════════════════════════════════════════════════════
"""
def spawn_rtl_power(freq_start, freq_stop, freq_step, gain=20):
    '''Spawn rtl_power for real spectrum sweep'''
    cmd = [
        'rtl_power',
        '-f', f'{freq_start}M:{freq_stop}M:{freq_step}k',
        '-i', '1',  # 1 second intervals
        '-g', str(gain),
        '-d', '0',  # Device 0
        '-e', '60s',  # 60 second capture
        '-'  # stdout
    ]
    print(f"[spectrum] rtl_power: {' '.join(cmd)}", file=sys.stderr, flush=True)
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

def parse_rtl_power_output(line):
    '''Parse rtl_power CSV format: date,time,hz_low,hz_high,hz_step,samples,...'''
    try:
        parts = line.split(',')
        if len(parts) < 6:
            return None

        hz_low = int(parts[2])
        hz_high = int(parts[3])
        hz_step = int(parts[4])
        power_values = [float(x) for x in parts[6:]]  # Rest are power readings

        return {
            'freq_start_mhz': hz_low / 1e6,
            'freq_stop_mhz': hz_high / 1e6,
            'freq_step_mhz': hz_step / 1e6,
            'power_db': power_values
        }
    except Exception as e:
        print(f"[spectrum] Parse error: {e}", file=sys.stderr)
        return None

def get_real_spectrum(freq_start, freq_stop, freq_step):
    '''Get real spectrum from rtl_power'''
    # TODO: Implement when rtl_power available
    pass
"""

# ═══════════════════════════════════════════════════════════════════════════
# TEST MODE: Fake Spectrum Generator (CURRENT)
# ═══════════════════════════════════════════════════════════════════════════

def generate_fake_spectrum(freq_start, freq_stop, freq_step):
    """Generate realistic FM band spectrum with peaks"""
    # FM stations (realistic peaks)
    fm_stations = [
        (89.1, -25),   # Istanbul FM
        (91.5, -28),   # Radio One
        (94.0, -26),   # NTV FM
        (96.5, -27),   # Power FM
        (99.2, -29),   # Metro FM
        (102.5, -30),  # Another station
        (105.0, -24),  # Strong station
    ]

    # Generate frequency array
    num_bins = int((freq_stop - freq_start) / freq_step) + 1
    power = [-85 + random.uniform(-5, 5) for _ in range(num_bins)]  # Noise floor

    # Add station peaks
    for station_freq, station_power in fm_stations:
        if freq_start <= station_freq <= freq_stop:
            idx = int((station_freq - freq_start) / freq_step)
            if 0 <= idx < len(power):
                # Gaussian peak
                for i in range(max(0, idx - 3), min(len(power), idx + 4)):
                    distance = abs(i - idx)
                    peak_power = station_power + (5 * (1 - (distance / 3)))
                    power[i] = max(power[i], peak_power)

    # Detect peaks (top 5)
    peaks = []
    for i, p in enumerate(power):
        if i > 0 and i < len(power) - 1:
            if p > power[i - 1] and p > power[i + 1] and p > -70:
                freq = freq_start + i * freq_step
                peaks.append({'frequency_mhz': round(freq, 3), 'power_db': round(p, 1)})

    peaks = sorted(peaks, key=lambda x: x['power_db'], reverse=True)[:5]

    return {
        'type': 'spectrum',
        'frequency_range': {
            'start_mhz': freq_start,
            'stop_mhz': freq_stop,
            'step_khz': freq_step * 1000
        },
        'power_db': [round(p, 1) for p in power],
        'peaks': peaks,
        'max_power_db': max(power),
        'min_power_db': min(power),
        'mean_power_db': round(sum(power) / len(power), 1),
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }

def main():
    """Main loop"""
    try:
        args = sys.argv[1:]
        freq_start = 88.0
        freq_stop = 108.0
        freq_step = 0.05
        use_real_sdr = False

        # Parse arguments
        for i, arg in enumerate(args):
            if arg == '--start' and i + 1 < len(args):
                freq_start = float(args[i + 1])
            elif arg == '--stop' and i + 1 < len(args):
                freq_stop = float(args[i + 1])
            elif arg == '--step' and i + 1 < len(args):
                freq_step = float(args[i + 1]) / 1000  # Convert from kHz to MHz
            elif arg == '--real':
                use_real_sdr = True

        print(f"[spectrum_analyzer] Başlatıldı: {freq_start}-{freq_stop} MHz, step {freq_step*1000} kHz ({'' if not use_real_sdr else 'REAL'})",
              file=sys.stderr, flush=True)

        if use_real_sdr:
            print("[spectrum_analyzer] RTL-SDR mod: henüz implement edilmedi", file=sys.stderr, flush=True)
            use_real_sdr = False

        # TEST MODE: Generate fake spectrum
        iteration = 0
        while True:
            data = generate_fake_spectrum(freq_start, freq_stop, freq_step)
            print(json.dumps(data), flush=True)

            iteration += 1
            if iteration % 10 == 0:
                print(f"[spectrum_analyzer] {iteration} waterfall frame gönderildi",
                      file=sys.stderr, flush=True)

            time.sleep(0.5)  # 2 Hz waterfall refresh

    except KeyboardInterrupt:
        print("[spectrum_analyzer] Durduruldu", file=sys.stderr, flush=True)
        sys.exit(0)
    except Exception as e:
        print(f"[spectrum_analyzer] Hata: {e}", file=sys.stderr, flush=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
