#!/usr/bin/env python3
"""Whisper ile ses dosyası transkripsiyon — tek seferlik."""
import sys
import json
import argparse

try:
    import whisper
except ImportError as e:
    print(json.dumps({"status": "error", "message": str(e)}), flush=True)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Ses dosyası yolu')
    parser.add_argument('--language', default=None)
    args = parser.parse_args()

    try:
        model = whisper.load_model("base")
        result = model.transcribe(args.file, language=args.language, fp16=False)
        print(json.dumps({
            "status": "final",
            "text": result["text"].strip(),
            "language": result.get("language", "unknown")
        }), flush=True)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}), flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
