#!/usr/bin/env python3
"""
OpenAI Whisper offline speech-to-text service for HABER X SIGINT
Reads PCM audio from stdin, transcribes with Whisper, outputs JSON
Supports: Türkçe, English, 99+ languages with auto-detection
"""

import sys
import json
import io
import numpy as np

try:
    import whisper
except ImportError as e:
    print(json.dumps({
        "status": "error",
        "message": f"Whisper not installed: {e}"
    }), flush=True)
    sys.exit(1)


class WhisperTranscriber:
    """Offline speech-to-text using OpenAI Whisper"""

    def __init__(self):
        self.model = None
        self.audio_buffer = []
        self.sample_rate = 16000
        self.buffer_duration = 3
        self.language = None  # argparse'tan gelir

    def initialize(self):
        """Load Whisper model"""
        try:
            # Load base model (supports 99+ languages including Turkish)
            print(json.dumps({
                "status": "loading",
                "model": "base"
            }), flush=True)

            self.model = whisper.load_model("base")

            print(json.dumps({
                "status": "initialized",
                "model": "whisper-base",
                "languages": ["Turkish", "English", "All"]
            }), flush=True)
            return True
        except Exception as e:
            print(json.dumps({
                "status": "error",
                "message": str(e)
            }), flush=True)
            return False

    def process_audio_chunk(self, chunk_bytes):
        """Convert 16-bit PCM bytes to float32 audio"""
        try:
            # Convert bytes to int16 array
            audio_int16 = np.frombuffer(chunk_bytes, dtype=np.int16)

            # Convert to float32 (-1.0 to 1.0)
            audio_float32 = audio_int16.astype(np.float32) / 32768.0

            # Add to buffer
            self.audio_buffer.append(audio_float32)

            # Check if we have enough audio (10 seconds @ 16kHz = 160,000 samples)
            total_samples = sum(len(chunk) for chunk in self.audio_buffer)
            buffer_samples = self.sample_rate * self.buffer_duration

            if total_samples >= buffer_samples:
                self.transcribe_buffer()
                self.audio_buffer = []

        except Exception as e:
            print(json.dumps({
                "status": "error",
                "message": f"Audio processing error: {e}"
            }), flush=True)

    def transcribe_buffer(self):
        """Transcribe accumulated audio"""
        if not self.audio_buffer or not self.model:
            return

        try:
            # Combine buffer into single array
            audio_data = np.concatenate(self.audio_buffer)

            # Transcribe with auto-language detection
            result = self.model.transcribe(
                audio_data,
                language=self.language,
                fp16=False
            )

            text = result["text"].strip()
            language = result.get("language", "unknown")

            if text:
                print(json.dumps({
                    "status": "final",
                    "text": text,
                    "language": language,
                    "confidence": result.get("confidence", 0)
                }), flush=True)

        except Exception as e:
            print(json.dumps({
                "status": "error",
                "message": f"Transcription error: {e}"
            }), flush=True)


def main():
    """Main service loop"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', default=None)
    args = parser.parse_args()

    transcriber = WhisperTranscriber()
    transcriber.language = args.language  # None = otomatik algıla

    if not transcriber.initialize():
        sys.exit(1)

    # Read PCM audio from stdin in chunks
    try:
        chunk_size = 4096  # Read 4KB at a time
        while True:
            chunk = sys.stdin.buffer.read(chunk_size)
            if not chunk:
                # End of input: process final buffer
                if transcriber.audio_buffer:
                    transcriber.transcribe_buffer()
                break

            transcriber.process_audio_chunk(chunk)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": str(e)
        }), flush=True)


if __name__ == "__main__":
    main()
