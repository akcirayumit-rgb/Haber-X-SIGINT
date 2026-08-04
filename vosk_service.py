#!/usr/bin/env python3
"""
Vosk offline speech-to-text service for HABER X SIGINT
Reads audio from stdin (Web Audio API -> Electron -> Python)
"""

import sys
import json
from pathlib import Path

try:
    from vosk import Model, KaldiRecognizer
except ImportError as e:
    print(json.dumps({
        "status": "error",
        "message": f"Vosk not installed: {e}"
    }), flush=True)
    sys.exit(1)


class SpeechRecognizer:
    """Offline speech recognizer using Vosk"""

    def __init__(self):
        self.model = None
        self.recognizer = None
        self.model_path = None

    def initialize(self):
        """Initialize recognizer with speech model"""
        # Find Vosk model
        model_base = Path.home() / '.vosk-models'
        if not model_base.exists():
            print(json.dumps({
                "status": "error",
                "message": "No Vosk models found. Run setup_vosk.py"
            }), flush=True)
            return False

        # Prefer small model
        preferred_models = ['small', 'en-us', 'model']
        for subdir in sorted(model_base.iterdir()):
            if subdir.is_dir() and 'vosk-model' in subdir.name:
                if 'small' in subdir.name.lower():
                    self.model_path = str(subdir)
                    break
                elif not self.model_path:
                    self.model_path = str(subdir)

        if not self.model_path:
            print(json.dumps({
                "status": "error",
                "message": "No Vosk model found"
            }), flush=True)
            return False

        try:
            self.model = Model(self.model_path)
            self.recognizer = KaldiRecognizer(self.model, 16000)
            print(json.dumps({
                "status": "initialized",
                "model_path": self.model_path
            }), flush=True)
            return True
        except Exception as e:
            print(json.dumps({
                "status": "error",
                "message": str(e)
            }), flush=True)
            return False

    def process_audio_stream(self):
        """Process audio from stdin (binary PCM 16-bit 16kHz)"""
        try:
            last_partial = ''
            while True:
                # Read audio chunk from stdin (4096 bytes = 2048 samples at 16-bit)
                data = sys.stdin.buffer.read(4096)
                if not data:
                    break

                # Feed audio to recognizer
                if hasattr(self.recognizer, 'accept_waveform'):
                    result = self.recognizer.accept_waveform(data)
                else:
                    result = self.recognizer.AcceptWaveform(data)

                if result:
                    # Final result
                    result_str = self.recognizer.Result()
                    result_obj = json.loads(result_str)
                    if 'result' in result_obj and result_obj['result']:
                        text_parts = []
                        for item in result_obj['result']:
                            if isinstance(item, dict):
                                word = item.get('conf', '')
                            else:
                                word = str(item)
                            if word and word != '0':
                                text_parts.append(word)
                        text = ' '.join(text_parts)
                        if text.strip():
                            print(json.dumps({
                                "status": "final",
                                "text": text.strip()
                            }), flush=True)
                    # Reset recognizer
                    self.recognizer = KaldiRecognizer(self.model, 16000)
                    last_partial = ''
                else:
                    # Partial result
                    partial_str = self.recognizer.PartialResult()
                    partial = json.loads(partial_str)
                    if 'partial' in partial:
                        current_partial = partial['partial'].strip()
                        if current_partial and current_partial != last_partial:
                            print(json.dumps({
                                "status": "interim",
                                "text": current_partial
                            }), flush=True)
                            last_partial = current_partial

        except BrokenPipeError:
            pass
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(json.dumps({
                "status": "error",
                "message": str(e)
            }), flush=True)


def main():
    """Main entry point"""
    recognizer = SpeechRecognizer()

    if recognizer.initialize():
        recognizer.process_audio_stream()
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
