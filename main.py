# main.py
# Desktop entry point — PyQt6 shell embedding Streamlit via WebEngine

import sys
import os
import subprocess
import threading
import tempfile
import shutil
import urllib.request
import socket

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings

# Resolve paths relative to *this* file so it works from any CWD
_HERE = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, _HERE)
from streamlit_app import get_streamlit_code

STREAMLIT_CODE = get_streamlit_code()


class WhiteHoleDesktop(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window icon (absolute path — works from any CWD)
        icon_path = os.path.join(_HERE, "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setWindowTitle("White Hole Project — Kalim Ghost Horn Observatory")
        self.resize(1680, 1000)

        self.temp_dir = tempfile.mkdtemp(prefix="whitehole_")
        self.port = self._get_free_port()
        self.process = None

        # Layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self.status_label = QLabel("Launching Kalim Ghost Horn Observatory …")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #06060e;
                color: #00FF7F;
                font-size: 17px;
                padding: 24px;
            }
        """)
        self.status_label.setFont(QFont("Segoe UI", 15))
        layout.addWidget(self.status_label)

        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("background-color: #06060e;")
        layout.addWidget(self.web_view, stretch=1)

        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)

        self._start_streamlit()

    # ── helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _get_free_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    def _start_streamlit(self):
        def _run():
            # Write app code into temp dir
            app_path = os.path.join(self.temp_dir, "app.py")
            with open(app_path, "w", encoding="utf-8") as f:
                f.write(STREAMLIT_CODE)

            # Copy project modules so imports resolve
            for name in ("constants.py", "utils.py", "plot_functions.py"):
                src = os.path.join(_HERE, name)
                if os.path.exists(src):
                    shutil.copy2(src, self.temp_dir)

            # Copy plot/ package
            plot_src = os.path.join(_HERE, "plot")
            plot_dst = os.path.join(self.temp_dir, "plot")
            if os.path.isdir(plot_src):
                if os.path.exists(plot_dst):
                    shutil.rmtree(plot_dst)
                shutil.copytree(plot_src, plot_dst)

            # Streamlit config
            cfg_dir = os.path.join(self.temp_dir, ".streamlit")
            os.makedirs(cfg_dir, exist_ok=True)
            with open(os.path.join(cfg_dir, "config.toml"), "w", encoding="utf-8") as f:
                f.write(f"""
[server]
headless = true
enableCORS = false
enableXsrfProtection = false
address = "127.0.0.1"
port = {self.port}

[browser]
gatherUsageStats = false
""")
            with open(os.path.join(cfg_dir, "credentials.toml"), "w", encoding="utf-8") as f:
                f.write('[general]\nemail = ""\n')

            env = os.environ.copy()
            env["PYTHONPATH"] = _HERE + os.pathsep + env.get("PYTHONPATH", "")

            self.process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", app_path,
                 "--server.port", str(self.port),
                 "--server.address", "127.0.0.1",
                 "--server.headless", "true"],
                env=env,
                cwd=self.temp_dir,
            )

        threading.Thread(target=_run, daemon=True).start()
        QTimer.singleShot(4000, lambda: self._check_ready(retries=25))

    def _check_ready(self, retries=25):
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{self.port}/_stcore/health", timeout=2
            ):
                self.status_label.setText("Observatory ready — entering white-hole space …")
                QTimer.singleShot(600, self._load_page)
                return
        except Exception:
            if retries > 0:
                self.status_label.setText(f"Launching … ({retries}s)")
                QTimer.singleShot(1000, lambda: self._check_ready(retries - 1))
            else:
                self.status_label.setText(
                    "Launch failed — please verify streamlit & plotly are installed."
                )

    def _load_page(self):
        self.status_label.hide()
        self.web_view.load(QUrl(f"http://127.0.0.1:{self.port}"))

    # ── cleanup ──────────────────────────────────────────────────────────

    def closeEvent(self, event):
        if self.process:
            self.process.kill()
            try:
                self.process.wait(timeout=3)
            except Exception:
                try:
                    self.process.terminate()
                except Exception:
                    pass
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        event.accept()


# ─────────────────────────────────────────────────────────────────────────
def main() -> int:
    """Launch the optional PyQt6 desktop shell."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet("QMainWindow { background-color: #06060e; }")
    app.setFont(QFont("Segoe UI", 11))

    window = WhiteHoleDesktop()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
