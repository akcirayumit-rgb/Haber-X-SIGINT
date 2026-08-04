#!/usr/bin/env python3
"""
Helper script to download and extract Vosk models
Run this once: python3 setup_vosk.py
"""

import urllib.request
import zipfile
import json
import sys
from pathlib import Path

def setup_vosk_models():
    """Download and extract Vosk models"""
    model_base = Path.home() / '.vosk-models'
    model_base.mkdir(exist_ok=True, parents=True)

    # Check if model already exists
    for subdir in model_base.iterdir():
        if subdir.is_dir() and 'vosk-model' in subdir.name:
            print(f"✓ Vosk model already exists: {subdir.name}")
            return True

    print("📥 Downloading Vosk model (this may take a few minutes)...")

    # Try different models
    models = [
        {
            "name": "English (en-us)",
            "url": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.42-gigaspeech.zip",
            "size": "~900MB"
        },
        {
            "name": "English (lightweight)",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
            "size": "~40MB"
        }
    ]

    for model_info in models:
        print(f"\n Trying: {model_info['name']} ({model_info['size']})...")
        try:
            model_zip = model_base / "model.zip"
            print(f"   Downloading...")

            # Use a progress callback
            def download_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                percent = min(downloaded * 100 // total_size, 100)
                print(f"   Progress: {percent}%", end='\r')

            urllib.request.urlretrieve(
                model_info['url'],
                model_zip,
                reporthook=download_progress
            )
            print("\n   ✓ Downloaded, extracting...")

            # Extract
            with zipfile.ZipFile(model_zip, 'r') as zip_ref:
                zip_ref.extractall(model_base)

            model_zip.unlink()
            print("   ✓ Extraction complete")

            # Verify
            for subdir in model_base.iterdir():
                if subdir.is_dir() and 'vosk-model' in subdir.name:
                    print(f"\n✓ Setup successful! Model: {subdir.name}")
                    return True

        except Exception as e:
            print(f"   ✗ Failed: {e}")
            continue

    print("\n✗ Failed to download any Vosk model")
    print("\nPlease download manually from:")
    print("  https://alphacephei.com/vosk/models")
    print("\nThen extract to:")
    print(f"  {model_base}")
    return False

if __name__ == '__main__':
    success = setup_vosk_models()
    sys.exit(0 if success else 1)
