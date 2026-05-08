#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import venv
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


APP_TITLE = "GLKVM App Builder"
PRIMARY_REQUIREMENTS = "PySide6>=6.8,<7"
APP_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">
  <rect width="128" height="128" rx="24" fill="#1f2933"/>
  <rect x="16" y="24" width="96" height="60" rx="10" fill="#2d3748"/>
  <rect x="24" y="32" width="80" height="44" rx="6" fill="#0f1720"/>
  <circle cx="38" cy="100" r="7" fill="#97a6ba"/>
  <circle cx="64" cy="100" r="7" fill="#97a6ba"/>
  <circle cx="90" cy="100" r="7" fill="#97a6ba"/>
  <path d="M34 54h22" stroke="#46c3a5" stroke-width="6" stroke-linecap="round"/>
  <path d="M72 48l14 10-14 10" fill="none" stroke="#46c3a5" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "glkvm-app"


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def ensure_https(address: str) -> str:
    value = address.strip()
    if not value:
        return value
    if value.startswith(("http://", "https://")):
        return value
    return f"https://{value}"


def build_viewer_html(name: str, target_url: str) -> str:
    title = name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe_url = target_url.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return textwrap.dedent(
        f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>{title}</title>
          <style>
            :root {{
              color-scheme: dark;
              --bg: #11161c;
              --panel: #1c242d;
              --edge: #2a3440;
              --text: #eef2f7;
              --muted: #9ba9bb;
              --accent: #46c3a5;
            }}
            * {{
              box-sizing: border-box;
            }}
            body {{
              margin: 0;
              min-height: 100vh;
              font-family: "DejaVu Sans", "Noto Sans", sans-serif;
              color: var(--text);
              background:
                radial-gradient(circle at top, rgba(70, 195, 165, 0.16), transparent 35%),
                linear-gradient(180deg, #11161c, #0a0e13);
            }}
            main {{
              display: grid;
              grid-template-rows: auto 1fr;
              min-height: 100vh;
            }}
            header {{
              display: flex;
              align-items: center;
              justify-content: space-between;
              gap: 1rem;
              padding: 1rem 1.25rem;
              border-bottom: 1px solid var(--edge);
              background: rgba(17, 22, 28, 0.9);
              backdrop-filter: blur(14px);
            }}
            .label {{
              display: flex;
              flex-direction: column;
              gap: 0.2rem;
            }}
            .label strong {{
              font-size: 1.05rem;
              letter-spacing: 0.03em;
            }}
            .label span {{
              color: var(--muted);
              font-size: 0.9rem;
            }}
            .status {{
              color: var(--muted);
              font-size: 0.82rem;
              text-align: right;
            }}
            section {{
              padding: 1rem;
            }}
            .frame-shell {{
              height: calc(100vh - 96px);
              border: 1px solid var(--edge);
              border-radius: 18px;
              overflow: hidden;
              background: var(--panel);
              box-shadow: 0 24px 60px rgba(0, 0, 0, 0.36);
            }}
            iframe {{
              width: 100%;
              height: 100%;
              border: 0;
              background: #000;
            }}
          </style>
        </head>
        <body>
          <main>
            <header>
              <div class="label">
                <strong>{title}</strong>
                <span>GLKVM Viewer Wrapper</span>
              </div>
              <div class="status">Source: {safe_url}</div>
            </header>
            <section>
              <div class="frame-shell">
                <iframe src="{safe_url}" title="{title}" referrerpolicy="no-referrer"></iframe>
              </div>
            </section>
          </main>
        </body>
        </html>
        """
    )


def build_generated_app(name: str, target_url: str) -> str:
    payload = json.dumps({"name": name, "target_url": target_url})
    return textwrap.dedent(
        f"""\
        #!/usr/bin/env python3
        from __future__ import annotations

        import json
        import os
        import sys
        from pathlib import Path

        existing_flags = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "").strip()
        extra_flag = "--ignore-certificate-errors"
        if extra_flag not in existing_flags.split():
            os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (existing_flags + " " + extra_flag).strip()

        from PySide6.QtCore import QUrl, Qt
        from PySide6.QtGui import QAction, QColor, QIcon, QPalette
        from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar
        from PySide6.QtWebEngineCore import QWebEnginePage
        from PySide6.QtWebEngineWidgets import QWebEngineView

        CONFIG = json.loads({payload!r})


        class KvmPage(QWebEnginePage):
            def certificateError(self, error):
                try:
                    error.acceptCertificate()
                except AttributeError:
                    pass
                return True


        class KvmWindow(QMainWindow):
            def __init__(self) -> None:
                super().__init__()
                self.setWindowTitle(CONFIG["name"])
                self.resize(1440, 900)

                toolbar = QToolBar("Navigation")
                toolbar.setMovable(False)
                toolbar.setFloatable(False)
                toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
                toolbar.setStyleSheet(
                    "QToolBar {{ spacing: 8px; padding: 8px; border: 0; background: #182029; }}"
                    "QToolButton {{ color: #e5ecf5; background: #253140; border: 1px solid #314153; "
                    "border-radius: 9px; padding: 8px 14px; font-weight: 600; }}"
                    "QToolButton:hover {{ background: #304155; }}"
                )
                self.addToolBar(Qt.LeftToolBarArea, toolbar)

                self.web = QWebEngineView(self)
                self.page = KvmPage(self.web)
                self.web.setPage(self.page)
                self.setCentralWidget(self.web)

                refresh_action = QAction("Refresh", self)
                refresh_action.triggered.connect(self.web.reload)
                toolbar.addAction(refresh_action)

                self.web.load(QUrl(CONFIG["target_url"]))


        def main() -> int:
            app = QApplication(sys.argv)
            app.setApplicationName(CONFIG["name"])
            app.setDesktopFileName(CONFIG["name"])

            palette = QPalette()
            palette.setColor(QPalette.Window, QColor("#10161d"))
            palette.setColor(QPalette.WindowText, QColor("#f1f5f9"))
            palette.setColor(QPalette.Base, QColor("#10161d"))
            palette.setColor(QPalette.AlternateBase, QColor("#182029"))
            palette.setColor(QPalette.ToolTipBase, QColor("#182029"))
            palette.setColor(QPalette.ToolTipText, QColor("#f1f5f9"))
            palette.setColor(QPalette.Text, QColor("#f1f5f9"))
            palette.setColor(QPalette.Button, QColor("#1d2630"))
            palette.setColor(QPalette.ButtonText, QColor("#f1f5f9"))
            palette.setColor(QPalette.Highlight, QColor("#46c3a5"))
            palette.setColor(QPalette.HighlightedText, QColor("#08120f"))
            app.setPalette(palette)

            icon_path = Path(__file__).resolve().parent / "icon.svg"
            if icon_path.exists():
                app.setWindowIcon(QIcon(str(icon_path)))

            window = KvmWindow()
            if icon_path.exists():
                window.setWindowIcon(QIcon(str(icon_path)))
            window.show()
            return app.exec()


        if __name__ == "__main__":
            raise SystemExit(main())
        """
    )


def build_launcher_script(app_dir: Path) -> str:
    return textwrap.dedent(
        f"""\
        #!/usr/bin/env bash
        set -euo pipefail
        SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
        if [[ -z "${{QT_QPA_PLATFORM:-}}" ]]; then
          if [[ "${{XDG_SESSION_TYPE:-}}" == "wayland" ]]; then
            export QT_QPA_PLATFORM=wayland
          fi
        fi
        export QTWEBENGINE_CHROMIUM_FLAGS="${{QTWEBENGINE_CHROMIUM_FLAGS:-}} --ignore-certificate-errors"
        exec "$SCRIPT_DIR/venv/bin/python3" "$SCRIPT_DIR/app.py"
        """
    )


def build_generated_requirements() -> str:
    return PRIMARY_REQUIREMENTS + "\n"


def build_desktop_file(name: str, script_path: Path, icon_path: Path) -> str:
    return textwrap.dedent(
        f"""\
        [Desktop Entry]
        Version=1.0
        Type=Application
        Name={name}
        Comment=Launch the {name} GLKVM view
        Exec="{script_path}"
        Icon={icon_path}
        Terminal=false
        Categories=Network;Utility;
        StartupNotify=true
        """
    )


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(760, 560)

        wrapper = QWidget(self)
        self.setCentralWidget(wrapper)

        title = QLabel("Build focused GLKVM launcher apps")
        title.setObjectName("heroTitle")

        subtitle = QLabel(
            "Create a standalone KVM viewer folder, a local HTML wrapper, and a desktop-searchable launcher."
        )
        subtitle.setWordWrap(True)
        subtitle.setObjectName("heroSubtitle")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Example: glkvm mono")

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Example: 10.0.0.154")

        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("Example: /home/user/Desktop")

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_output_directory)

        create_button = QPushButton("Save and Create")
        create_button.setObjectName("primaryButton")
        create_button.clicked.connect(self.create_package)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setSpacing(14)
        form.addRow("Name", self.name_input)
        form.addRow("IP Address", self.ip_input)

        output_row = QHBoxLayout()
        output_row.addWidget(self.output_input, 1)
        output_row.addWidget(browse_button)
        output_widget = QWidget()
        output_widget.setLayout(output_row)
        form.addRow("Output Location", output_widget)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Generation log will appear here.")

        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(6)
        layout.addLayout(form)
        layout.addWidget(create_button)
        layout.addWidget(self.log, 1)

        self.apply_styles()

    def apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
              background:
                qlineargradient(x1:0, y1:0, x2:1, y2:1,
                  stop:0 #10161d, stop:0.55 #151d26, stop:1 #1c2732);
              color: #eef2f7;
              font-family: "DejaVu Sans";
              font-size: 14px;
            }
            QLabel#heroTitle {
              font-size: 28px;
              font-weight: 700;
              color: #f5f7fb;
            }
            QLabel#heroSubtitle {
              color: #a4b1c2;
              font-size: 14px;
            }
            QLineEdit, QTextEdit {
              background: rgba(16, 22, 29, 0.96);
              border: 1px solid #344153;
              border-radius: 12px;
              padding: 10px 12px;
              selection-background-color: #46c3a5;
              selection-color: #08120f;
            }
            QLineEdit:focus, QTextEdit:focus {
              border: 1px solid #46c3a5;
            }
            QPushButton {
              background: #263241;
              border: 1px solid #364658;
              border-radius: 12px;
              padding: 10px 16px;
              font-weight: 600;
            }
            QPushButton:hover {
              background: #314153;
            }
            QPushButton#primaryButton {
              background: #46c3a5;
              color: #08120f;
              border: 0;
              padding: 12px 18px;
              font-size: 15px;
            }
            QPushButton#primaryButton:hover {
              background: #56d6b6;
            }
            """
        )

    def browse_output_directory(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select Output Location")
        if selected:
            self.output_input.setText(selected)

    def append_log(self, message: str) -> None:
        self.log.append(message)
        QApplication.processEvents()

    def validate_inputs(self) -> tuple[str, str, Path] | None:
        name = self.name_input.text().strip()
        ip_address = self.ip_input.text().strip()
        output_text = os.path.expanduser(self.output_input.text().strip())

        if not name or not ip_address or not output_text:
            QMessageBox.warning(self, APP_TITLE, "Name, IP address, and output location are required.")
            return None

        output_dir = Path(output_text)
        return name, ensure_https(ip_address), output_dir

    def run_command(self, command: list[str], cwd: Path | None = None) -> None:
        self.append_log("$ " + " ".join(shell_quote(part) for part in command))
        completed = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.stdout.strip():
            self.append_log(completed.stdout.strip())
        if completed.returncode != 0:
            if completed.stderr.strip():
                self.append_log(completed.stderr.strip())
            raise RuntimeError(f"Command failed with exit code {completed.returncode}: {' '.join(command)}")
        if completed.stderr.strip():
            self.append_log(completed.stderr.strip())

    def create_package(self) -> None:
        validated = self.validate_inputs()
        if not validated:
            return

        name, target_url, output_dir = validated
        slug = slugify(name)
        app_dir = output_dir / slug
        desktop_dir = Path.home() / ".local/share/applications"
        desktop_path = desktop_dir / f"{slug}.desktop"

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            desktop_dir.mkdir(parents=True, exist_ok=True)
            if app_dir.exists():
                shutil.rmtree(app_dir)
            app_dir.mkdir(parents=True, exist_ok=True)

            self.append_log(f"Creating package at {app_dir}")

            (app_dir / "viewer.html").write_text(build_viewer_html(name, target_url), encoding="utf-8")
            (app_dir / "app.py").write_text(build_generated_app(name, target_url), encoding="utf-8")
            (app_dir / "requirements.txt").write_text(build_generated_requirements(), encoding="utf-8")
            (app_dir / "icon.svg").write_text(APP_ICON_SVG, encoding="utf-8")

            launcher_path = app_dir / "run_glkvm.sh"
            launcher_path.write_text(build_launcher_script(app_dir), encoding="utf-8")
            launcher_path.chmod(0o755)

            self.append_log("Creating isolated runtime environment for the generated app")
            venv.create(app_dir / "venv", with_pip=True)

            pip_path = app_dir / "venv/bin/pip"
            python_path = app_dir / "venv/bin/python3"
            self.run_command([str(pip_path), "install", "--upgrade", "pip"], cwd=app_dir)
            self.run_command([str(pip_path), "install", "-r", str(app_dir / "requirements.txt")], cwd=app_dir)

            desktop_content = build_desktop_file(name, launcher_path, app_dir / "icon.svg")
            (app_dir / f"{slug}.desktop").write_text(desktop_content, encoding="utf-8")
            desktop_path.write_text(desktop_content, encoding="utf-8")
            desktop_path.chmod(0o755)

            update_desktop_db = shutil.which("update-desktop-database")
            if update_desktop_db:
                self.run_command([update_desktop_db, str(desktop_dir)])
            self.run_command([str(python_path), "-m", "py_compile", str(app_dir / "app.py")], cwd=app_dir)

            self.append_log("")
            self.append_log("Generation completed successfully.")
            self.append_log(f"Launcher folder: {app_dir}")
            self.append_log(f"Search entry: {desktop_path}")
            QMessageBox.information(
                self,
                APP_TITLE,
                f"Created {name}.\n\nFolder: {app_dir}\nDesktop entry: {desktop_path}",
            )
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, APP_TITLE, str(exc))
            self.append_log(f"ERROR: {exc}")


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
