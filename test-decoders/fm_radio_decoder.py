#!/usr/bin/env python3
"""
Multi-Band Radio Decoder — RTL-SDR Hardware (rtl_fm subprocess)

REAL MODE (active):
  - Uses rtl_fm subprocess for direct tuning
  - Real signal strength from tuner output
  - Multi-band support: FM/AM/HF/DAB scanning
  - Non-blocking audio playback (Popen) to prevent dropout

Hardware:
  - NESDR Smart (RTL2832U)
  - Bypass kernel driver with rtl_fm
"""

import json
import sys
import subprocess
import time
import re
import signal
import os
import numpy as np
from datetime import datetime, timezone

# Global audio process tracking (non-blocking playback)
audio_process = None
audio_pid = None

# Multi-band frequency ranges (MHz)
BAND_RANGES = {
    'fm': {'min': 88, 'max': 108, 'label': 'FM Broadcast', 'bw': 200000, 'demod': 'fm'},
    'am': {'min': 0.52, 'max': 1.7, 'label': 'AM Broadcast', 'bw': 100000, 'demod': 'am'},
    'hf': {'min': 3, 'max': 30, 'label': 'Shortwave (HF)', 'bw': 50000, 'demod': 'ssb'},
    'dab': {'min': 174, 'max': 240, 'label': 'DAB+ Digital', 'bw': 1536000, 'demod': 'dab'}
}

# Known Turkish FM stations
FM_STATIONS = {
    88.2: "TRT Radyo 1", 89.1: "Istanbul FM", 91.5: "Radio One", 94.0: "NTV FM",
    94.9: "Power FM", 96.5: "Power FM", 99.2: "Metro FM", 100.2: "Show FM",
    102.5: "Radyo Klas", 103.3: "Radyo D", 105.0: "Best FM", 106.2: "Virgin Radio"
}

def measure_signal_strength(freq_mhz):
    """Measure signal strength at frequency using rtl_fm"""
    try:
        cmd = [
            "rtl_fm", "-f", f"{freq_mhz}M",
            "-s", "200000",
            "-g", "25",
            "-M", "fm",
            "-t", "raw"
        ]

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(0.1)  # Let tuner settle

        # Read stderr for tuner info
        proc_check = subprocess.run(
            ["rtl_fm", "-f", f"{freq_mhz}M", "-s", "22050", "-r", "22050", "-g", "25", "-t", "raw"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2
        )

        # Parse stderr for gain value
        stderr = proc_check.stderr
        gain_match = re.search(r'Tuner gain set to ([\d.]+)', stderr)

        if gain_match:
            gain = float(gain_match.group(1))
            snr = 10 + gain  # Estimate SNR from gain setting
        else:
            snr = 20  # Default reasonable signal

        proc.kill()
        return snr

    except subprocess.TimeoutExpired:
        return 15
    except Exception as e:
        print(f"[fm_radio] Measurement error: {e}", file=sys.stderr)
        return 10

def scan_fm_spectrum(freq_start, freq_stop, freq_step):
    """rtl_power ile gerçek bant taraması yapar.

    Önceki sürüm her frekans için sabit 20 dB döndürüyordu (gain regex'i
    tutmayınca varsayılan değer), eşik 12 olduğu için de BÜTÜN frekanslar
    "istasyon" sayılıyordu. Bu yüzden listede her kanal tam olarak 20 dB
    görünüyordu. rtl_power gerçek güç spektrumu verir.
    """
    print(f"[fm_radio] RTL-SDR TARAMA: {freq_start}-{freq_stop} MHz", file=sys.stderr, flush=True)

    step_hz = int(freq_step * 1e6)
    cmd = ['rtl_power',
           '-f', f'{freq_start}M:{freq_stop}M:{step_hz}',
           '-g', '40',
           '-i', '1',       # 1 saniyelik integrasyon
           '-1']            # tek geçiş, sonra çık

    print(f"[fm_radio] {' '.join(cmd)}", file=sys.stderr, flush=True)

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, timeout=180)
    except subprocess.TimeoutExpired:
        print("[fm_radio] Tarama zaman aşımına uğradı", file=sys.stderr, flush=True)
        return
    except Exception as e:
        print(f"[fm_radio] Tarama başlatılamadı: {e}", file=sys.stderr, flush=True)
        return

    if not proc.stdout.strip():
        err = (proc.stderr or '').strip().splitlines()
        print(f"[fm_radio] Tarama verisi yok: {err[-1] if err else 'bilinmeyen hata'}",
              file=sys.stderr, flush=True)
        return

    # rtl_power CSV: tarih, saat, HzDüşük, HzYüksek, HzAdım, örnek, dB, dB, ...
    powers = []   # (freq_hz, db)
    for line in proc.stdout.splitlines():
        parts = [p.strip() for p in line.split(',')]
        if len(parts) < 7:
            continue
        try:
            low, high, step = float(parts[2]), float(parts[3]), float(parts[4])
            for i, val in enumerate(parts[6:]):
                db = float(val)
                if db == db:   # NaN değil
                    powers.append((low + i * step, db))
        except ValueError:
            continue

    if not powers:
        print("[fm_radio] Tarama çözümlenemedi", file=sys.stderr, flush=True)
        return

    # Gürültü tabanına göre eşik: taban + 6 dB
    dbs = sorted(p[1] for p in powers)
    noise_floor = dbs[len(dbs) // 2]        # medyan
    threshold = noise_floor + 6.0
    print(f"[fm_radio] Gürültü tabanı {noise_floor:.1f} dB, eşik {threshold:.1f} dB",
          file=sys.stderr, flush=True)

    # Kanal ızgarasına topla, her kanalın tepe değerini al
    channels = {}
    for hz, db in powers:
        if db < threshold:
            continue
        mhz = round(hz / 1e6 / freq_step) * freq_step
        if not (freq_start <= mhz <= freq_stop):
            continue
        key = round(mhz, 2)
        if db > channels.get(key, -999):
            channels[key] = db

    for mhz in sorted(channels, key=lambda k: -channels[k]):
        db = channels[mhz]
        snr = round(db - noise_floor, 1)
        data = {
            "frequency_mhz": mhz,
            "station_name": FM_STATIONS.get(round(mhz, 1), "Bilinmiyor"),
            "program_service": "FM",
            "snr_db": snr,
            "signal_strength": max(0, min(100, int(snr * 3))),
            "rds_available": False,
            "radio_text": f"Tepe: {db:.1f} dB (taban üstü +{snr:.1f})",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        print(f"[JSON]:{json.dumps(data)}", file=sys.stderr, flush=True)

    print(f"[fm_radio] {len(channels)} kanal bulundu", file=sys.stderr, flush=True)

def sweep_band(freq_start, freq_stop, bin_khz=100, gain='40'):
    """Bandı sürekli tarar ve her tam geçişi RF panoraması olarak yayınlar.

    Tek tuner olduğu için bu mod çalışırken ses çalınamaz; kullanıcı
    waterfall'dan bir frekans seçtiğinde dinleme moduna geçilir.
    """
    global audio_process, audio_pid

    cmd = ['rtl_power', '-f', f'{freq_start}M:{freq_stop}M:{bin_khz}k',
           '-g', str(gain), '-i', '1', '-']
    print(f"[fm_radio] PANORAMA: {' '.join(cmd)}", file=sys.stderr, flush=True)

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            text=True, preexec_fn=os.setsid)
    audio_process = proc          # stop_audio() bunu da temizlesin
    audio_pid = proc.pid

    segments = {}      # low_hz -> [dB...]
    last_low = None
    sweeps = 0

    def publish():
        """Toplanan hop'ları tek sürekli spektruma birleştirip yayınla"""
        if not segments:
            return
        spectrum = []
        for low in sorted(segments):
            spectrum.extend(segments[low])
        peak_i = max(range(len(spectrum)), key=lambda i: spectrum[i])
        span = freq_stop - freq_start
        peak_mhz = round(freq_start + span * peak_i / max(1, len(spectrum) - 1), 2)

        print("[JSON]:" + json.dumps({
            "mode": "sweep",
            "freq_start_mhz": freq_start,
            "freq_stop_mhz": freq_stop,
            "spectrum_db": [round(v, 1) for v in spectrum],
            "peak_mhz": peak_mhz,
            "peak_db": round(spectrum[peak_i], 1),
            "frequency_mhz": peak_mhz,
            "station_name": FM_STATIONS.get(round(peak_mhz, 1), "Bilinmiyor"),
            "program_service": "PANORAMA",
            "snr_db": round(spectrum[peak_i], 1),
            "radio_text": f"En güçlü: {peak_mhz} MHz ({spectrum[peak_i]:.1f} dB)",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), file=sys.stderr, flush=True)

    try:
        for line in proc.stdout:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 7:
                continue
            try:
                low = float(parts[2])
                dbs = [float(v) for v in parts[6:] if v]
            except ValueError:
                continue

            # low başa döndüyse bir tam tarama tamamlanmıştır
            if last_low is not None and low < last_low:
                publish()
                sweeps += 1
                if sweeps == 1:
                    print(f"[fm_radio] Panorama akışı başladı "
                          f"({freq_start}-{freq_stop} MHz)", file=sys.stderr, flush=True)
                segments = {}

            segments[low] = dbs
            last_low = low

    except KeyboardInterrupt:
        pass
    finally:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except Exception:
            pass
        if sweeps == 0:
            print("[fm_radio] HATA: rtl_power veri üretmedi "
                  "(cihaz bağlı mı? 'rtl_test -t')", file=sys.stderr, flush=True)


def stop_audio():
    """Stop background audio playback"""
    global audio_process, audio_pid

    if audio_process is not None:
        try:
            print(f"[fm_radio] Ses yayını durduruluyor (PID: {audio_pid})...", file=sys.stderr, flush=True)
            # Süreç grubunu öldür — aksi halde rtl_fm arkada kalıp
            # tuner'ı kilitler ve sonraki tune "No supported devices" verir
            try:
                os.killpg(os.getpgid(audio_process.pid), signal.SIGTERM)
            except Exception:
                audio_process.terminate()
            try:
                audio_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(os.getpgid(audio_process.pid), signal.SIGKILL)
                except Exception:
                    audio_process.kill()
            audio_process = None
            audio_pid = None
        except Exception as e:
            print(f"[fm_radio] Audio stop error: {e}", file=sys.stderr, flush=True)

AUDIO_RATE = 32000        # rtl_fm -M wbfm çıkış hızı
FFT_SIZE = 2048           # ~16 waterfall karesi/saniye
SPECTRUM_BINS = 48        # Waterfall sütun sayısı


def build_sox_effects(settings):
    """UI'daki preamp / filtre / gürültü kesme kontrollerini sox efektlerine çevirir.

    Bu kontroller daha önce yalnızca console.log yapıyordu; artık ses
    zincirine gerçekten uygulanıyorlar.
    """
    fx = []

    preamp = float(settings.get('preamp_db') or 0)
    if abs(preamp) > 0.01:
        fx += ['vol', f'{preamp}dB']

    ftype = (settings.get('filter_type') or 'none').lower()
    if 'high' in ftype:
        fx += ['highpass', '300']
    elif 'low' in ftype:
        fx += ['lowpass', '3000']
    elif 'band' in ftype:
        fx += ['highpass', '300', 'lowpass', '3000']

    if settings.get('noise_cancel'):
        # Konuşma bandına daralt + dinamik sıkıştırma (sox noisered profil
        # dosyası ister; canlı akışta profil yok, bu yaklaşım profilsiz çalışır)
        # UI hem Türkçe hem İngilizce değer gönderebiliyor
        mode = (settings.get('noise_mode') or 'orta').lower()
        strength = {
            'düşük': '0.2', 'dusuk': '0.2', 'low': '0.2',
            'orta': '0.4', 'medium': '0.4',
            'yüksek': '0.6', 'yuksek': '0.6', 'high': '0.6',
        }.get(mode, '0.4')
        fx += ['highpass', '200', 'lowpass', '3400',
               'compand', '0.1,0.3', f'-60,-60,-30,-15,-20,-{strength}', '-5']

    return fx


def audio_and_spectrum_loop(frequency, band, settings):
    """rtl_fm çıktısını hem sox'a (ses) hem numpy FFT'ye (waterfall) besler.

    Tek tuner var, bu yüzden ses ve spektrum aynı akıştan türetiliyor.
    Yayınlanan spektrum SES bandıdır (0-16 kHz), RF taraması değil.
    """
    global audio_process, audio_pid

    demod = 'am' if band == 'am' else ('usb' if band == 'hf' else 'wbfm')
    gain = settings.get('gain', 'auto')

    rtl_cmd = ['rtl_fm', '-f', f'{frequency}M', '-M', demod,
               '-s', '200000', '-r', str(AUDIO_RATE)]
    if gain != 'auto':
        rtl_cmd += ['-g', str(gain)]
    ppm = int(settings.get('ppm') or 0)
    if ppm:
        rtl_cmd += ['-p', str(ppm)]

    sox_cmd = ['play', '-t', 'raw', '-r', str(AUDIO_RATE),
               '-e', 'signed', '-b', '16', '-c', '1', '-q', '-']
    sox_cmd += build_sox_effects(settings)

    print(f"[fm_radio] RF : {' '.join(rtl_cmd)}", file=sys.stderr, flush=True)
    print(f"[fm_radio] SES: {' '.join(sox_cmd)}", file=sys.stderr, flush=True)

    rtl = subprocess.Popen(rtl_cmd, stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, preexec_fn=os.setsid)
    sox = subprocess.Popen(sox_cmd, stdin=subprocess.PIPE,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           preexec_fn=os.setsid)

    audio_process = rtl
    audio_pid = rtl.pid

    station_name = FM_STATIONS.get(round(frequency, 1), "Bilinmiyor")
    window = np.hanning(FFT_SIZE)
    chunk_bytes = FFT_SIZE * 2   # 16-bit örnekler
    got_data = False

    try:
        while True:
            raw = rtl.stdout.read(chunk_bytes)
            if not raw or len(raw) < chunk_bytes:
                break

            if not got_data:
                got_data = True
                print(f"[fm_radio] Ses akışı başladı ({frequency} MHz)",
                      file=sys.stderr, flush=True)

            # Sesi çalmaya gönder
            try:
                sox.stdin.write(raw)
                sox.stdin.flush()
            except (BrokenPipeError, ValueError):
                print("[fm_radio] Ses çıkışı kapandı", file=sys.stderr, flush=True)
                break

            # Aynı örneklerden gerçek FFT → waterfall
            samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
            # Genlik normalizasyonu: 0 dB = tam ölçek (dBFS).
            # (2/N faktörü FFT ölçeği, /0.5 Hanning pencere kazanç telafisi)
            spec = np.abs(np.fft.rfft(samples * window))[:FFT_SIZE // 2]
            spec = spec * 2.0 / (FFT_SIZE * 0.5)
            binned = spec[:SPECTRUM_BINS * (len(spec) // SPECTRUM_BINS)]
            binned = binned.reshape(SPECTRUM_BINS, -1).mean(axis=1)
            spectrum_db = 20 * np.log10(binned + 1e-9)

            rms = float(np.sqrt(np.mean(samples ** 2)))
            snr = round(20 * np.log10(rms + 1e-9) + 60, 1)

            data = {
                "frequency_mhz": round(frequency, 2),
                "band": band,
                "station_name": station_name,
                "program_service": band.upper(),
                "snr_db": snr,
                "signal_strength": max(0, min(100, int(snr * 2))),
                "spectrum_db": [round(float(v), 1) for v in spectrum_db],
                "spectrum_max_hz": AUDIO_RATE // 2,
                "rds_available": False,
                "radio_text": f"Ses seviyesi: {snr:.1f} dB",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            print(f"[JSON]:{json.dumps(data)}", file=sys.stderr, flush=True)

    except KeyboardInterrupt:
        pass
    finally:
        for p in (rtl, sox):
            try:
                os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            except Exception:
                pass
        if not got_data:
            print("[fm_radio] HATA: rtl_fm hiç veri üretmedi "
                  "(cihaz bağlı mı? 'rtl_test -t' ile kontrol edin)",
                  file=sys.stderr, flush=True)


def tune_radio(frequency, band='fm', settings=None):
    """Frekansa geç: ses çal + gerçek spektrum yayınla (akış bitene kadar bloklar)"""
    settings = settings or {}
    print(f"[fm_radio] {frequency} MHz'e ayarlanıyor ({band.upper()})...",
          file=sys.stderr, flush=True)

    try:
        stop_audio()
        audio_and_spectrum_loop(frequency, band, settings)

    except Exception as e:
        print(f"[fm_radio] Tuning error: {e}", file=sys.stderr, flush=True)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Band Radio Decoder for RTL-SDR (NESDR Smart)")
    parser.add_argument("--band", default="fm", choices=['fm', 'am', 'hf', 'dab'],
                        help="Radio band: fm, am, hf, or dab")
    parser.add_argument("--freq", type=float, default=100.0, help="Tune frequency (MHz)")
    parser.add_argument("--scan-start", type=float, help="Scan start frequency (MHz)")
    parser.add_argument("--scan-stop", type=float, help="Scan stop frequency (MHz)")
    parser.add_argument("--scan-step", type=float, default=0.5, help="Scan step (MHz)")
    parser.add_argument("--sample-rate", type=int, default=2400000, help="Sample rate")
    parser.add_argument("--bandwidth", type=int, default=200000, help="Bandwidth")
    parser.add_argument("--gain", default="25", help="Gain (dB)")
    parser.add_argument("--ppm", type=int, default=0, help="PPM correction")
    parser.add_argument("--demod", default="fm_wide", help="Demodulation type")
    # Ses işleme zinciri (UI kontrolleri)
    parser.add_argument("--preamp-db", type=float, default=0, help="Preamplifier gain (dB)")
    parser.add_argument("--filter-type", default="none", help="Audio filter: high-pass/low-pass/band-pass/none")
    parser.add_argument("--noise-cancel", action="store_true", help="Enable noise reduction")
    parser.add_argument("--noise-mode", default="orta", help="Noise reduction strength")

    args = parser.parse_args()

    # Validate band
    if args.band not in BAND_RANGES:
        print(f"[fm_radio] ERROR: Band '{args.band}' not supported. Use: fm, am, hf, dab", file=sys.stderr, flush=True)
        sys.exit(1)

    band_info = BAND_RANGES[args.band]
    print(f"[fm_radio] RADYO BANDI: {band_info['label']} ({band_info['min']}-{band_info['max']} MHz)", file=sys.stderr, flush=True)
    print(f"[fm_radio] RTL-SDR AYARLARI: SR={args.sample_rate/1e6:.1f}MHz, " +
          f"BW={args.bandwidth/1e3:.0f}kHz, Gain={args.gain}dB, PPM={args.ppm}",
          file=sys.stderr, flush=True)

    # Signal handlers for cleanup
    def signal_handler(sig, frame):
        print(f"[fm_radio] Signal {sig} alındı, durduruluyur...", file=sys.stderr, flush=True)
        stop_audio()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    if args.scan_start and args.scan_stop:
        # Sürekli RF panoraması: waterfall'da frekans ekseni boyunca akar,
        # kullanıcı üzerine tıklayarak istediği kanala geçebilir
        print(f"[fm_radio] PANORAMA MODU: {args.scan_start}-{args.scan_stop} MHz",
              file=sys.stderr, flush=True)
        try:
            sweep_band(args.scan_start, args.scan_stop,
                       bin_khz=max(25, int(args.scan_step * 1000)),
                       gain=(args.gain if args.gain != 'auto' else '40'))
        except KeyboardInterrupt:
            stop_audio()
    else:
        print(f"[fm_radio] AYAR MODU: {args.freq} MHz ({args.band.upper()})", file=sys.stderr, flush=True)
        # tune_radio artık akış boyunca bloklar (ses + spektrum yayını),
        # bu yüzden ayrıca bekleme döngüsü gerekmiyor
        try:
            tune_radio(args.freq, args.band, {
                'gain': args.gain,
                'ppm': args.ppm,
                'preamp_db': args.preamp_db,
                'filter_type': args.filter_type,
                'noise_cancel': args.noise_cancel,
                'noise_mode': args.noise_mode,
            })
        except KeyboardInterrupt:
            stop_audio()
