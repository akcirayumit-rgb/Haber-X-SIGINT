#!/usr/bin/env python3
"""
Haber-X SIGINT — PyQt6 Desktop Application
Masaüstü uygulması: Express server + PyQt window
"""

import sys
import os
import subprocess
import time
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QTimer


class HaberXSIGINT(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Haber-X SIGINT — Sinyal İstihbarat Konsolu")
        self.setGeometry(100, 100, 1400, 900)

        # Web view
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)

        # Express server process
        self.server_process = None
        self.start_server()

        # Load localhost:3000 (wait for server)
        QTimer.singleShot(2000, self.load_app)

    def start_server(self):
        """Start Express server in background"""
        try:
            script_dir = Path(__file__).parent
            self.server_process = subprocess.Popen(
                ['node', str(script_dir / 'server.js')],
                cwd=str(script_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("[PyQt] Express server başlatıldı")
        except Exception as e:
            print(f"[PyQt] Server start error: {e}")

    def load_app(self):
        """Load Express app in web view"""
        self.browser.load(QUrl("http://localhost:3000"))
        print("[PyQt] App localhost:3000 yükleniyor...")

    def closeEvent(self, event):
        """Stop server when app closes"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait(timeout=5)
            print("[PyQt] Server kapatıldı")
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = HaberXSIGINT()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
