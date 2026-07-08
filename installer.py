import os
import sys
import shutil
import subprocess
from pathlib import Path

# Initialize installer entry

# Associate taskbar icon on Windows
if sys.platform == "win32":
    import ctypes
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("whitebox.wboxai.v1")
    except Exception:
        pass
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QUrl
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QStackedWidget,
    QProgressBar,
    QCheckBox,
    QFormLayout,
    QMessageBox,
    QRadioButton,
    QGraphicsDropShadowEffect,
    QTextEdit,
)
from PyQt6.QtGui import QFont, QColor, QIcon, QPainter, QLinearGradient

# ----------------- DESIGN STYLESHEET -----------------
THEME_CSS = """
QMainWindow {
    background-color: #121824;
}
QWidget#central_widget {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #121824, stop:1 #1e293b);
}
QLabel {
    color: #e2e8f0;
    font-family: "Segoe UI", Arial, sans-serif;
}
QLabel#title {
    font-size: 24px;
    font-weight: bold;
    color: #ffffff;
}
QLabel#subtitle {
    font-size: 14px;
    color: #94a3b8;
}
QLabel#section_title {
    font-size: 16px;
    font-weight: 600;
    color: #38bdf8;
    margin-top: 10px;
    margin-bottom: 5px;
}
QLineEdit {
    background-color: #0f172a;
    color: #f1f5f9;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    font-family: "Segoe UI", sans-serif;
}
QLineEdit:focus {
    border: 1px solid #38bdf8;
    background-color: #1e293b;
}
QPushButton {
    background-color: #1e293b;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #334155;
    color: #ffffff;
}
QPushButton#primary {
    background-color: #0284c7;
    color: #ffffff;
    border: 1px solid #0369a1;
}
QPushButton#primary:hover {
    background-color: #0ea5e9;
}
QPushButton#primary:disabled {
    background-color: #1e293b;
    color: #64748b;
    border: 1px solid #334155;
}
QProgressBar {
    border: 1px solid #334155;
    border-radius: 8px;
    background-color: #0f172a;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
}
QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0ea5e9, stop:1 #2563eb);
    border-radius: 7px;
}
QCheckBox {
    color: #cbd5e1;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 4px;
}
QCheckBox::indicator:checked {
    background-color: #0284c7;
    border: 1px solid #38bdf8;
}
"""

class InstallWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, dest_dir, config_data):
        super().__init__()
        self.dest_dir = Path(dest_dir)
        self.config_data = config_data

    def run(self):
        try:
            self.progress.emit(10, "Preparing installation...")
            self.msleep(300)

            # Determine source directory
            frozen = getattr(sys, "frozen", False)
            if frozen:
                # Inside PyInstaller package, the app folder contains our main build files
                src_dir = Path(sys._MEIPASS) / "app"
            else:
                # In development, look for dist/main
                src_dir = Path(__file__).resolve().parent / "dist" / "main"
                if not src_dir.exists():
                    # Fallback to copy workspace files for simulation
                    src_dir = Path(__file__).resolve().parent

            self.progress.emit(20, "Creating target directory...")
            self.dest_dir.mkdir(parents=True, exist_ok=True)
            self.msleep(200)

            # Copy files if we have a source folder
            self.progress.emit(30, "Copying application files...")
            if src_dir.exists() and src_dir.resolve() != self.dest_dir.resolve():
                if src_dir.is_dir():
                    # Copy contents recursively
                    for item in src_dir.iterdir():
                        # Skip venv, build, dist, .git, and installer files
                        if item.name in ("venv", "build", "dist", ".git", "installer.py", "installer.spec", "Setup.exe"):
                            continue
                        
                        dst_item = self.dest_dir / item.name
                        if item.is_dir():
                            if dst_item.exists():
                                shutil.rmtree(dst_item)
                            shutil.copytree(item, dst_item)
                        else:
                            shutil.copy2(item, dst_item)
                else:
                    # If src is a single file (like just wboxai.exe), copy it directly
                    shutil.copy2(src_dir, self.dest_dir / "wboxai.exe")
            self.progress.emit(60, "Writing configuration settings...")
            self.msleep(300)

            # Generate or update .env content
            existing_env = {}
            env_file = self.dest_dir / ".env"
            if env_file.is_file():
                try:
                    from dotenv import dotenv_values
                    existing_env = dict(dotenv_values(env_file))
                except Exception:
                    pass

            updates = {
                "LIGHTWEIGHT_MODE": "true",
                "MAX_WORKERS": "1",
                "OPENAI_API_KEY": self.config_data.get("openai_key", ""),
                "GEMINI_API_KEY": self.config_data.get("gemini_key", ""),
                "CLAUDE_API_KEY": self.config_data.get("claude_key", ""),
                "JOB_ROLE": self.config_data.get("job_role", "Software Engineer"),
                "JOB_DESCRIPTION": self.config_data.get("job_desc", ""),
                "CODE_LANGUAGE": self.config_data.get("code_lang", "python"),
                "CODING_MODE": "auto",
                "AUDIO_SOURCE": "loopback",
                "ENTERPRISE_AUDIO": "true",
                "AUDIO_STT_PROVIDER": "speech_to_text",
                "SPEECH_TO_TEXT_SERVER_URL": "ws://127.0.0.1:8000",
                "SPEECH_TO_TEXT_PROVIDER": "deepgram",
                "SCREEN_WATCH_ENABLED": "false",
                "EMAIL_RECEIVER": self.config_data.get("email_recv", ""),
                "SMTP_SERVER": self.config_data.get("smtp_server", "smtp.gmail.com"),
                "SMTP_PORT": self.config_data.get("smtp_port", "587"),
                "SMTP_USERNAME": self.config_data.get("smtp_user", ""),
                "SMTP_PASSWORD": self.config_data.get("smtp_pass", ""),
                "SMTP_USE_TLS": "true",
            }

            for k, v in updates.items():
                if k not in existing_env or v:
                    existing_env[k] = v

            env_lines = ["# Created by WboxAI Setup Wizard"]
            for k, v in existing_env.items():
                env_lines.append(f"{k}={v}")

            env_file.write_text("\n".join(env_lines), encoding="utf-8")

            wboxai_app_dir = self.dest_dir / "wboxai_app"
            if wboxai_app_dir.is_dir():
                (wboxai_app_dir / ".env").write_text("\n".join(env_lines), encoding="utf-8")

            # Create default empty context files if they don't exist
            self.progress.emit(75, "Creating local context templates...")
            intro_val = self.config_data.get("intro_text", "").strip() or "Enter details about yourself for introductions."
            contexts = {
                "resume_context.txt": "Paste your resume plain text here.",
                "intro_context.txt": intro_val,
                "project_overview.txt": "Add details of major projects you worked on."
            }
            for name, content in contexts.items():
                p = self.dest_dir / name
                if name == "intro_context.txt" or not p.is_file():
                    p.write_text(content, encoding="utf-8")
                
                # Check wboxai_app folder as well
                p_wboxai = wboxai_app_dir / name
                if wboxai_app_dir.is_dir() and (name == "intro_context.txt" or not p_wboxai.is_file()):
                    p_wboxai.write_text(content, encoding="utf-8")

            # Shortcuts creation
            self.progress.emit(90, "Creating system shortcuts...")
            self.msleep(300)
            
            # Determine wboxai.exe location
            main_exe_path = self.dest_dir / "wboxai.exe"
            if not main_exe_path.is_file() and (self.dest_dir / "main.py").is_file():
                # If we copied script, target python launcher (shouldn't happen in frozen setup)
                main_exe_path = self.dest_dir / "main.py"

            if main_exe_path.exists():
                self.create_windows_shortcuts(main_exe_path)

            self.progress.emit(100, "Installation complete!")
            self.finished.emit(True, "Success")
        except Exception as e:
            self.finished.emit(False, str(e))

    def create_windows_shortcuts(self, target_path: Path):
        try:
            desktop_path = Path(os.environ["USERPROFILE"]) / "Desktop" / "WboxAI.lnk"
            start_menu_dir = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            start_menu_dir.mkdir(parents=True, exist_ok=True)
            start_shortcut = start_menu_dir / "WboxAI.lnk"

            # Determine shortcut icon location
            icon_location = target_path
            ico_file = target_path.parent / "wboxai_app" / "logo.ico"
            if ico_file.is_file():
                icon_location = ico_file
            elif (target_path.parent / "logo.ico").is_file():
                icon_location = target_path.parent / "logo.ico"

            for lnk in (desktop_path, start_shortcut):
                # Executing powershell to create lnk natively
                ps_cmd = f"""
                $Shell = New-Object -ComObject WScript.Shell
                $Shortcut = $Shell.CreateShortcut('{str(lnk)}')
                $Shortcut.TargetPath = '{str(target_path)}'
                $Shortcut.WorkingDirectory = '{str(target_path.parent)}'
                $Shortcut.IconLocation = '{str(icon_location)}'
                $Shortcut.Save()
                """
                subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, check=True)
        except Exception as shortcut_err:
            print(f"Error creating shortcuts: {shortcut_err}")


class SetupWizard(QMainWindow):
    closed = pyqtSignal()

    def __init__(self, config_only=False, first_time_setup=False):
        super().__init__()
        self.config_only = config_only
        self.first_time_setup = first_time_setup
        self.setup_successful = False
        self.config_data = {}
        
        self.setWindowTitle("WboxAI Setup")
        self.setFixedSize(620, 520)
        
        # Load window icon
        frozen = getattr(sys, "frozen", False)
        if frozen:
            logo_path = Path(sys._MEIPASS) / "wboxai_app" / "logo.png"
        else:
            logo_path = Path(__file__).resolve().parent / "wboxai_app" / "logo.png"
        if logo_path.is_file():
            self.setWindowIcon(QIcon(str(logo_path)))
        
        # Central Widget & Shadow Layout
        self.central = QWidget(self)
        self.central.setObjectName("central_widget")
        self.setCentralWidget(self.central)
        
        self.main_layout = QVBoxLayout(self.central)
        self.central.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(25, 25, 25, 20)
        self.main_layout.setSpacing(15)
        
        # Header Area
        self.header_layout = QHBoxLayout()
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(40, 40)
        if logo_path.is_file():
            from PyQt6.QtGui import QPixmap
            pixmap = QPixmap(str(logo_path))
            self.logo_label.setPixmap(pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        self.title_layout = QVBoxLayout()
        self.title_label = QLabel("WboxAI Setup")
        self.title_label.setObjectName("title")
        self.subtitle_label = QLabel("Configure and install your enterprise interview assistant.")
        self.subtitle_label.setObjectName("subtitle")
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addWidget(self.subtitle_label)
        
        self.header_layout.addWidget(self.logo_label)
        self.header_layout.addSpacing(10)
        self.header_layout.addLayout(self.title_layout)
        self.header_layout.addStretch()
        self.main_layout.addLayout(self.header_layout)
        
        # Divider Line
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #334155;")
        self.main_layout.addWidget(line)
        
        # QStackedWidget Pages
        self.pages = QStackedWidget()
        self.main_layout.addWidget(self.pages)
        
        # Footer Navigation
        self.footer_layout = QHBoxLayout()
        self.btn_back = QPushButton("Back")
        self.btn_back.clicked.connect(self.prev_page)
        self.btn_next = QPushButton("Next")
        self.btn_next.setObjectName("primary")
        self.btn_next.clicked.connect(self.next_page)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.close)
        
        self.footer_layout.addWidget(self.btn_back)
        self.footer_layout.addStretch()
        self.footer_layout.addWidget(self.btn_next)
        self.footer_layout.addWidget(self.btn_cancel)
        self.main_layout.addLayout(self.footer_layout)
        
        # Create Wizard Pages
        self.create_pages()
        self.update_navigation()

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

    def create_pages(self):
        # 1. Welcome Page
        self.page_welcome = QWidget()
        layout = QVBoxLayout(self.page_welcome)
        layout.setContentsMargins(10, 10, 10, 10)
        desc = QLabel(
            "Welcome to the WboxAI Setup Wizard!\n\n"
            "This installer will configure your API integration settings, setup transcripts, "
            "and deploy the software on your machine.\n\n"
            "Features:\n"
            "• Transparent overlay displaying real-time hints & coding solutions.\n"
            "• Capture exclusion on Windows (hidden from screenshares like Zoom or Teams).\n"
            "• Multi-provider AI fallback (OpenAI, Gemini, Claude).\n"
            "• Smart session tracking and email transcript reporting."
        )
        desc.setWordWrap(True)
        desc.setFont(QFont("Segoe UI", 11))
        layout.addWidget(desc)
        layout.addStretch()
        self.pages.addWidget(self.page_welcome)

        # 2. Path Page
        self.page_path = QWidget()
        layout = QVBoxLayout(self.page_path)
        layout.setContentsMargins(10, 10, 10, 10)
        
        label_path_title = QLabel("Select Installation Folder")
        label_path_title.setObjectName("section_title")
        layout.addWidget(label_path_title)
        
        label_path_desc = QLabel("Please choose where to install the application files:")
        layout.addWidget(label_path_desc)
        
        path_input_layout = QHBoxLayout()
        self.edit_path = QLineEdit()
        default_install_dir = Path.home() / "AppData" / "Local" / "Programs" / "WboxAI"
        self.edit_path.setText(str(default_install_dir))
        self.btn_browse = QPushButton("Browse...")
        self.btn_browse.clicked.connect(self.browse_folder)
        path_input_layout.addWidget(self.edit_path)
        path_input_layout.addWidget(self.btn_browse)
        layout.addLayout(path_input_layout)
        
        layout.addStretch()
        self.pages.addWidget(self.page_path)

        # 3. AI Config Page
        self.page_ai = QWidget()
        layout = QVBoxLayout(self.page_ai)
        layout.setContentsMargins(10, 10, 10, 10)
        
        label_ai_title = QLabel("AI Engine Configuration")
        label_ai_title.setObjectName("section_title")
        layout.addWidget(label_ai_title)
        
        form = QFormLayout()
        form.setSpacing(10)
        
        self.edit_openai = QLineEdit()
        self.edit_openai.setPlaceholderText("sk-...")
        self.edit_openai.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.edit_gemini = QLineEdit()
        self.edit_gemini.setPlaceholderText("Gemini API Key (Optional)")
        self.edit_gemini.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.edit_claude = QLineEdit()
        self.edit_claude.setPlaceholderText("Claude API Key (Optional)")
        self.edit_claude.setEchoMode(QLineEdit.EchoMode.Password)
        
        form.addRow("OpenAI Key (Required):", self.edit_openai)
        form.addRow("Gemini Key:", self.edit_gemini)
        form.addRow("Claude Key:", self.edit_claude)
        
        # Load existing .env values if they exist
        self.load_existing_keys()
        
        layout.addLayout(form)
        layout.addStretch()
        self.pages.addWidget(self.page_ai)

        # 4. Settings Page (Job role, language, email credentials)
        self.page_settings = QWidget()
        layout = QVBoxLayout(self.page_settings)
        layout.setContentsMargins(10, 10, 10, 10)
        
        label_settings_title = QLabel("Job & Email Integration Settings")
        label_settings_title.setObjectName("section_title")
        layout.addWidget(label_settings_title)
        
        form = QFormLayout()
        form.setSpacing(8)
        
        self.edit_role = QLineEdit()
        self.edit_role.setText(self.config_data.get("job_role", "Software Engineer"))
        
        self.edit_lang = QLineEdit()
        self.edit_lang.setText(self.config_data.get("code_lang", "python"))
        
        self.edit_email = QLineEdit()
        self.edit_email.setPlaceholderText("recipient@example.com (Optional)")
        self.edit_email.setText(self.config_data.get("email_recv", ""))
        
        self.edit_smtp_server = QLineEdit()
        self.edit_smtp_server.setText(self.config_data.get("smtp_server", "smtp.gmail.com"))
        
        self.edit_smtp_user = QLineEdit()
        self.edit_smtp_user.setText(self.config_data.get("smtp_user", ""))
        
        self.edit_smtp_pass = QLineEdit()
        self.edit_smtp_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.edit_smtp_pass.setText(self.config_data.get("smtp_pass", ""))
        
        self.edit_intro = QTextEdit()
        self.edit_intro.setPlaceholderText("Paste your candidate introduction / past technologies here...")
        self.edit_intro.setMaximumHeight(85)
        existing_intro = self.load_existing_intro()
        if existing_intro:
            self.edit_intro.setPlainText(existing_intro)
        
        form.addRow("Job Target Role:", self.edit_role)
        form.addRow("Coding Language:", self.edit_lang)
        form.addRow("Candidate Intro:", self.edit_intro)
        form.addRow("Email Report Recipient:", self.edit_email)
        form.addRow("SMTP Server Host:", self.edit_smtp_server)
        form.addRow("SMTP Login Username:", self.edit_smtp_user)
        form.addRow("SMTP Login Password:", self.edit_smtp_pass)
        
        layout.addLayout(form)
        layout.addStretch()
        self.pages.addWidget(self.page_settings)

        # 5. Progress Page
        self.page_progress = QWidget()
        layout = QVBoxLayout(self.page_progress)
        layout.setContentsMargins(10, 10, 10, 10)
        
        label_progress_title = QLabel("Installing Components")
        label_progress_title.setObjectName("section_title")
        layout.addWidget(label_progress_title)
        
        self.progress_label = QLabel("Ready to start copying files...")
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        self.pages.addWidget(self.page_progress)

        # 6. Finished Page
        self.page_finished = QWidget()
        layout = QVBoxLayout(self.page_finished)
        layout.setContentsMargins(10, 10, 10, 10)
        
        label_fin_title = QLabel("Setup Complete")
        label_fin_title.setObjectName("section_title")
        layout.addWidget(label_fin_title)
        
        self.fin_desc = QLabel(
            "Congratulations! WboxAI has been successfully configured and installed.\n\n"
            "You can launch the program from your Desktop shortcut or start menu program group."
        )
        self.fin_desc.setWordWrap(True)
        self.fin_desc.setFont(QFont("Segoe UI", 11))
        layout.addWidget(self.fin_desc)
        
        self.chk_launch = QCheckBox("Launch WboxAI now")
        self.chk_launch.setChecked(True)
        layout.addWidget(self.chk_launch)
        
        layout.addStretch()
        self.pages.addWidget(self.page_finished)

        # 7. Selection Page
        self.page_selection = QWidget()
        self._setup_selection_page()
        self.pages.addWidget(self.page_selection)

        # 8. Web Login Page
        self.page_web_login = QWidget()
        self._setup_web_login_page()
        self.pages.addWidget(self.page_web_login)

    def _setup_selection_page(self):
        layout = QVBoxLayout(self.page_selection)
        layout.setContentsMargins(10, 10, 10, 10)
        
        lbl_title = QLabel("Choose Setup Method")
        lbl_title.setObjectName("section_title")
        layout.addWidget(lbl_title)
        
        lbl_desc = QLabel("Select how you want to configure your WboxAI environment:")
        lbl_desc.setFont(QFont("Segoe UI", 11))
        layout.addWidget(lbl_desc)
        layout.addSpacing(25)
        
        self.btn_wbox_setup = QRadioButton("Setup with Wbox (Recommended)")
        self.btn_wbox_setup.setChecked(True)
        self.btn_wbox_setup.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn_wbox_setup.setStyleSheet("QRadioButton { color: #f8fafc; spacing: 8px; } QRadioButton::indicator { width: 18px; height: 18px; }")
        
        lbl_wbox_desc = QLabel(
            "   Sync automatically: log in to your Whitebox Learning account to\n"
            "   instantly retrieve your profile resume context and LLM API keys."
        )
        lbl_wbox_desc.setStyleSheet("color: #94a3b8; font-size: 11px; margin-left: 25px; margin-bottom: 20px;")
        
        self.btn_manual_setup = QRadioButton("Set up Manually")
        self.btn_manual_setup.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn_manual_setup.setStyleSheet("QRadioButton { color: #f8fafc; spacing: 8px; } QRadioButton::indicator { width: 18px; height: 18px; }")
        
        lbl_manual_desc = QLabel(
            "   Configure step-by-step: manually enter your own AI API keys\n"
            "   and customize target job credentials."
        )
        lbl_manual_desc.setStyleSheet("color: #94a3b8; font-size: 11px; margin-left: 25px;")
        
        layout.addWidget(self.btn_wbox_setup)
        layout.addWidget(lbl_wbox_desc)
        layout.addWidget(self.btn_manual_setup)
        layout.addWidget(lbl_manual_desc)
        layout.addStretch()

    def _setup_web_login_page(self):
        layout = QVBoxLayout(self.page_web_login)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        lbl_sync_title = QLabel("Whitebox Learning Sync")
        lbl_sync_title.setObjectName("section_title")
        layout.addWidget(lbl_sync_title)
        
        lbl_sync_desc = QLabel(
            "Log in to your Whitebox Learning account to instantly sync your "
            "profile configuration, target job details, and API keys."
        )
        lbl_sync_desc.setWordWrap(True)
        layout.addWidget(lbl_sync_desc)
        
        # Step 1: Open external browser
        btn_open_browser = QPushButton("1. Open Login Page in Browser")
        btn_open_browser.setObjectName("primary")
        btn_open_browser.clicked.connect(self.open_wbl_login_browser)
        layout.addWidget(btn_open_browser)
        
        # Step 2: Paste token
        lbl_token = QLabel("2. Paste your Wbox Auth Token / API Key here:")
        layout.addWidget(lbl_token)
        
        self.edit_wbox_token = QLineEdit()
        self.edit_wbox_token.setPlaceholderText("Paste your wbox_token here...")
        layout.addWidget(self.edit_wbox_token)
        
        # Step 3: Trigger Sync
        btn_trigger_sync = QPushButton("3. Sync Settings")
        btn_trigger_sync.clicked.connect(self.sync_wbl_profile)
        layout.addWidget(btn_trigger_sync)
        
        self.web_status_label = QLabel("Ready to sync...")
        self.web_status_label.setStyleSheet("color: #38bdf8; font-weight: bold;")
        self.web_status_label.setWordWrap(True)
        layout.addWidget(self.web_status_label)
        
        self.web_view = None
        layout.addStretch()

    def load_web_login(self):
        self.edit_wbox_token.clear()
        self.web_status_label.setText("Ready to sync. Click above to open the login page.")

    def open_wbl_login_browser(self):
        import webbrowser
        webbrowser.open("https://www.whitebox-learning.com/login")
        self.web_status_label.setText("Opened login page in browser. Please log in, copy your token from your dashboard/profile, and paste it below.")

    def sync_wbl_profile(self):
        token = self.edit_wbox_token.text().strip()
        if not token:
            QMessageBox.warning(self, "Validation Error", "Please paste your Wbox Auth Token first.")
            return
        
        self.web_status_label.setText("Syncing settings...")
        self.on_sync_data_extracted({"jwt_token": token})

    def fetch_data_from_wbl_backend(self, token):
        import urllib.request
        import urllib.error
        import json
        import ssl
        
        endpoints = [
            "https://www.whitebox-learning.com/api/candidate/sync",
            "https://www.whitebox-learning.com/api/wbox-sync",
            "https://www.whitebox-learning.com/api/wboxai/sync",
            "https://www.whitebox-learning.com/api/candidate/profile",
            "https://www.whitebox-learning.com/api/candidate/config",
        ]
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        for url in endpoints:
            # Try GET request
            try:
                req = urllib.request.Request(
                    url,
                    headers={"Authorization": f"Bearer {token}", "Accept": "application/json"}
                )
                with urllib.request.urlopen(req, context=ctx, timeout=8) as response:
                    if response.status == 200:
                        try:
                            return json.loads(response.read().decode("utf-8"))
                        except Exception:
                            pass
            except Exception as e:
                print(f"GET fetch from {url} failed: {e}")
                
            # Try POST request
            try:
                req = urllib.request.Request(
                    url,
                    data=b"{}",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                )
                with urllib.request.urlopen(req, context=ctx, timeout=8) as response:
                    if response.status == 200:
                        try:
                            return json.loads(response.read().decode("utf-8"))
                        except Exception:
                            pass
            except Exception as e:
                print(f"POST fetch from {url} failed: {e}")
                
        return None

    def on_sync_data_extracted(self, result):
        if hasattr(self, "web_view") and self.web_view:
            self.web_view.setEnabled(True)
        if not result:
            result = {}
            
        token = result.get("jwt_token")
        backend_data = None
        
        if token:
            self.web_status_label.setText("Token acquired! Syncing from WBL backend server...")
            backend_data = self.fetch_data_from_wbl_backend(token)
            
        # Parse combined data (backend + fallback local storage)
        combined = {}
        if isinstance(backend_data, dict):
            combined.update(backend_data)
            
        import json
        for k, v in result.items():
            if k == "jwt_token":
                continue
            if isinstance(v, str):
                try:
                    combined[k] = json.loads(v)
                except Exception:
                    combined[k] = v
                    
        openai_key = ""
        gemini_key = ""
        claude_key = ""
        resume = ""
        job_role = ""
        code_lang = ""
        
        def search_dict(d):
            nonlocal openai_key, gemini_key, claude_key, resume, job_role, code_lang
            if not isinstance(d, dict):
                return
            for k, v in d.items():
                k_lower = k.lower()
                if isinstance(v, str):
                    v_strip = v.strip()
                    if "openai" in k_lower or "open_ai" in k_lower:
                        if v_strip.startswith("sk-") and not openai_key:
                            openai_key = v_strip
                    elif "gemini" in k_lower:
                        if v_strip and not gemini_key:
                            gemini_key = v_strip
                    elif "claude" in k_lower or "anthropic" in k_lower:
                        if v_strip and not claude_key:
                            claude_key = v_strip
                    elif v_strip.startswith("sk-") and not openai_key:
                        openai_key = v_strip
                        
                    if "resume" in k_lower or "candidate_resume" in k_lower:
                        if len(v_strip) > len(resume):
                            resume = v_strip
                    if "role" in k_lower or "job" in k_lower:
                        if len(v_strip) < 100 and not job_role:
                            job_role = v_strip
                    if "lang" in k_lower or "language" in k_lower:
                        if len(v_strip) < 20 and not code_lang:
                            code_lang = v_strip
                elif isinstance(v, dict):
                    search_dict(v)
                elif isinstance(v, list):
                    for item in v:
                        if isinstance(item, dict):
                            search_dict(item)
                        elif isinstance(item, str):
                            if item.strip().startswith("sk-") and not openai_key:
                                openai_key = item.strip()

        search_dict(combined)
        
        import re
        raw_str = str(combined)
        sk_match = re.search(r"sk-[a-zA-Z0-9_-]{30,}", raw_str)
        if sk_match and not openai_key:
            openai_key = sk_match.group(0)
            
        if openai_key:
            self.edit_openai.setText(openai_key)
        if gemini_key:
            self.edit_gemini.setText(gemini_key)
        if claude_key:
            self.edit_claude.setText(claude_key)
        if job_role:
            self.edit_role.setText(job_role)
        if code_lang:
            self.edit_lang.setText(code_lang)
            
        if resume:
            self.config_data["resume_text"] = resume
            try:
                frozen = getattr(sys, "frozen", False)
                exe_dir = Path(sys.executable).resolve().parent if frozen else Path(__file__).resolve().parent
                (exe_dir / "resume_context.txt").write_text(resume, encoding="utf-8")
                wboxai_app_dir = exe_dir / "wboxai_app"
                if wboxai_app_dir.is_dir():
                    (wboxai_app_dir / "resume_context.txt").write_text(resume, encoding="utf-8")
            except Exception:
                pass

        if openai_key or gemini_key or claude_key or resume:
            QMessageBox.information(
                self,
                "Sync Complete",
                "Successfully retrieved configuration settings from your Wbox profile!\n\n"
                f"OpenAI Key: {'Configured' if openai_key else 'Not Found'}\n"
                f"Gemini Key: {'Configured' if gemini_key else 'Not Found'}\n"
                f"Claude Key: {'Configured' if claude_key else 'Not Found'}\n"
                f"Resume: {'Synced' if resume else 'Not Found'}"
            )
            self.pages.setCurrentIndex(3) # Move to settings verification page
            self.update_navigation()
        else:
            QMessageBox.warning(
                self,
                "Sync Partial",
                "Logged in, but could not automatically retrieve API keys or resume text from your profile.\n"
                "Please configure settings manually on the next page."
            )
            self.pages.setCurrentIndex(2) # Go to manual AI Config page
            self.update_navigation()

    def load_existing_keys(self):
        # Look for existing .env in the current working directory, or next to exe
        frozen = getattr(sys, "frozen", False)
        exe_dir = Path(sys.executable).resolve().parent if frozen else Path(__file__).resolve().parent
        
        # Check current folder or copilot_app subfolder
        env_paths = [
            exe_dir / ".env",
            exe_dir / "wboxai_app" / ".env"
        ]
        
        loaded = False
        for path in env_paths:
            if path.is_file():
                try:
                    from dotenv import dotenv_values
                    values = dotenv_values(path)
                    self.edit_openai.setText(values.get("OPENAI_API_KEY", ""))
                    self.edit_gemini.setText(values.get("GEMINI_API_KEY", ""))
                    self.edit_claude.setText(values.get("CLAUDE_API_KEY", ""))
                    self.config_data["job_role"] = values.get("JOB_ROLE", "Software Engineer")
                    self.config_data["code_lang"] = values.get("CODE_LANGUAGE", "python")
                    self.config_data["email_recv"] = values.get("EMAIL_RECEIVER", "")
                    self.config_data["smtp_server"] = values.get("SMTP_SERVER", "smtp.gmail.com")
                    self.config_data["smtp_port"] = values.get("SMTP_PORT", "587")
                    self.config_data["smtp_user"] = values.get("SMTP_USERNAME", "")
                    self.config_data["smtp_pass"] = values.get("SMTP_PASSWORD", "")
                    loaded = True
                    break
                except Exception:
                    pass
        
        if self.config_only:
            self.title_label.setText("WboxAI Configuration")
            self.subtitle_label.setText("Update your system integration settings and API keys.")

    def load_existing_intro(self) -> str:
        try:
            frozen = getattr(sys, "frozen", False)
            exe_dir = Path(sys.executable).resolve().parent if frozen else Path(__file__).resolve().parent
            intro_file = exe_dir / "intro_context.txt"
            if not intro_file.is_file():
                intro_file = exe_dir / "wboxai_app" / "intro_context.txt"
            if intro_file.is_file():
                return intro_file.read_text(encoding="utf-8").strip()
        except Exception:
            pass
        return ""

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Installation Folder", self.edit_path.text())
        if folder:
            self.edit_path.setText(folder)

    def update_navigation(self):
        idx = self.pages.currentIndex()
        
        # Configure Back button visibility
        if self.config_only:
            # Start page is index 6 (Choose Setup Method).
            self.btn_back.setVisible(idx in (7, 2, 3))
        elif self.first_time_setup:
            # Start page is index 0. Welcome -> Selection (6) -> Web Login (7) or AI Config (2).
            self.btn_back.setVisible(idx in (6, 7, 2, 3))
        else:
            # Standard installer. Welcome -> Path (1) -> Selection (6) -> Web Login (7) or AI Config (2).
            self.btn_back.setVisible(idx in (1, 6, 7, 2, 3))
            self.btn_cancel.setVisible(idx < 4) # Hide cancel once install process starts
            
        # Configure Next/Action button text
        if idx == 3:
            if self.config_only:
                self.btn_next.setText("Save")
            elif self.first_time_setup:
                self.btn_next.setText("Finish")
            else:
                self.btn_next.setText("Install")
        elif idx == 5:
            self.btn_next.setText("Finish")
            self.btn_back.setVisible(False)
        else:
            self.btn_next.setText("Next")
            
        # Disable buttons while progress is running
        if idx == 4:
            self.btn_back.setEnabled(False)
            self.btn_next.setEnabled(False)
            self.btn_cancel.setEnabled(False)
        else:
            self.btn_back.setEnabled(True)
            self.btn_next.setEnabled(True)
            self.btn_cancel.setEnabled(True)

    def prev_page(self):
        idx = self.pages.currentIndex()
        if self.config_only and idx == 6:
            return # Don't go back past selection screen in config-only
        if self.first_time_setup and idx == 6:
            self.pages.setCurrentIndex(0) # Back to Welcome from Selection
            self.update_navigation()
            return
        if idx == 7: # From Web Login, go back to Selection (6)
            self.pages.setCurrentIndex(6)
            self.update_navigation()
            return
        if idx == 2: # From AI Config, go back to Selection (6)
            self.pages.setCurrentIndex(6)
            self.update_navigation()
            return
        if idx == 6: # From Selection, go back to Path (1) in installer
            self.pages.setCurrentIndex(1)
            self.update_navigation()
            return
            
        self.pages.setCurrentIndex(idx - 1)
        self.update_navigation()

    def next_page(self):
        idx = self.pages.currentIndex()
        
        # Validation checks
        if idx == 1 and not (self.config_only or self.first_time_setup):
            path = self.edit_path.text().strip()
            if not path:
                QMessageBox.warning(self, "Validation Error", "Please specify a target installation directory.")
                return
            self.pages.setCurrentIndex(6) # Go to Selection page
            self.update_navigation()
            return
            
        if idx == 0:
            if self.config_only or self.first_time_setup:
                self.pages.setCurrentIndex(6) # Go to Selection page
            else:
                self.pages.setCurrentIndex(1) # Go to Path page
            self.update_navigation()
            return

        if idx == 6: # Selection Page
            if self.btn_wbox_setup.isChecked():
                self.load_web_login()
                self.pages.setCurrentIndex(7) # Go to Web Login page
            else:
                self.pages.setCurrentIndex(2) # Go to Manual AI Config page
            self.update_navigation()
            return

        if idx == 7: # Web Login page next button (fallback / skip)
            self.pages.setCurrentIndex(2)
            self.update_navigation()
            return
            
        if idx == 2: # AI Config validation
            key = self.edit_openai.text().strip()
            if not key or not key.startswith("sk-"):
                QMessageBox.warning(
                    self, 
                    "Validation Error", 
                    "An OpenAI API Key is required for speech transcription.\nIt must start with 'sk-'."
                )
                return

        # Save settings on next
        self.config_data["openai_key"] = self.edit_openai.text().strip()
        self.config_data["gemini_key"] = self.edit_gemini.text().strip()
        self.config_data["claude_key"] = self.edit_claude.text().strip()
        self.config_data["job_role"] = self.edit_role.text().strip()
        self.config_data["code_lang"] = self.edit_lang.text().strip()
        self.config_data["email_recv"] = self.edit_email.text().strip()
        self.config_data["smtp_server"] = self.edit_smtp_server.text().strip()
        self.config_data["smtp_user"] = self.edit_smtp_user.text().strip()
        self.config_data["smtp_pass"] = self.edit_smtp_pass.text().strip()
        self.config_data["smtp_port"] = "587"
        self.config_data["intro_text"] = self.edit_intro.toPlainText().strip()

        # Action: transitions
        if self.config_only:
            if idx == 2:
                self.pages.setCurrentIndex(3) # Settings Review
            elif idx == 3:
                self.save_configuration_only()
            elif idx == 5:
                self.close()
        elif self.first_time_setup:
            if idx == 2:
                self.pages.setCurrentIndex(3) # Settings Review
            elif idx == 3:
                self.save_configuration_locally()
                self.setup_successful = True
                self.close()
            elif idx == 5:
                self.close()
        else:
            if idx == 2:
                self.pages.setCurrentIndex(3) # Settings Review
            elif idx == 3:
                self.pages.setCurrentIndex(4) # Progress
                self.update_navigation()
                self.start_installation()
            elif idx == 5:
                if self.chk_launch.isChecked():
                    self.launch_app()
                self.close()
            else:
                self.pages.setCurrentIndex(idx + 1)
                
        self.update_navigation()

    def start_installation(self):
        self.worker = InstallWorker(self.edit_path.text().strip(), self.config_data)
        self.worker.progress.connect(self.on_install_progress)
        self.worker.finished.connect(self.on_install_finished)
        self.worker.start()

    def on_install_progress(self, val, msg):
        self.progress_bar.setValue(val)
        self.progress_label.setText(msg)

    def on_install_finished(self, success, msg):
        if success:
            self.pages.setCurrentIndex(5) # Done Page
        else:
            QMessageBox.critical(self, "Installation Failed", f"An error occurred during installation:\n{msg}")
            self.pages.setCurrentIndex(3) # Back to settings
        self.update_navigation()

    def save_configuration_only(self):
        try:
            frozen = getattr(sys, "frozen", False)
            exe_dir = Path(sys.executable).resolve().parent if frozen else Path(__file__).resolve().parent
            
            # Generate or update .env content
            existing_env = {}
            env_file = exe_dir / ".env"
            if env_file.is_file():
                try:
                    from dotenv import dotenv_values
                    existing_env = dict(dotenv_values(env_file))
                except Exception:
                    pass

            updates = {
                "LIGHTWEIGHT_MODE": "true",
                "MAX_WORKERS": "1",
                "OPENAI_API_KEY": self.config_data.get("openai_key", ""),
                "GEMINI_API_KEY": self.config_data.get("gemini_key", ""),
                "CLAUDE_API_KEY": self.config_data.get("claude_key", ""),
                "JOB_ROLE": self.config_data.get("job_role", "Software Engineer"),
                "JOB_DESCRIPTION": self.config_data.get("job_desc", ""),
                "CODE_LANGUAGE": self.config_data.get("code_lang", "python"),
                "CODING_MODE": "auto",
                "AUDIO_SOURCE": "loopback",
                "ENTERPRISE_AUDIO": "true",
                "AUDIO_STT_PROVIDER": "speech_to_text",
                "SPEECH_TO_TEXT_SERVER_URL": "ws://127.0.0.1:8000",
                "SPEECH_TO_TEXT_PROVIDER": "deepgram",
                "SCREEN_WATCH_ENABLED": "false",
                "EMAIL_RECEIVER": self.config_data.get("email_recv", ""),
                "SMTP_SERVER": self.config_data.get("smtp_server", "smtp.gmail.com"),
                "SMTP_PORT": self.config_data.get("smtp_port", "587"),
                "SMTP_USERNAME": self.config_data.get("smtp_user", ""),
                "SMTP_PASSWORD": self.config_data.get("smtp_pass", ""),
                "SMTP_USE_TLS": "true",
            }

            for k, v in updates.items():
                if k not in existing_env or v:
                    existing_env[k] = v

            env_lines = ["# Updated by WboxAI Setup Wizard"]
            for k, v in existing_env.items():
                env_lines.append(f"{k}={v}")

            env_file.write_text("\n".join(env_lines), encoding="utf-8")

            wboxai_app_dir = exe_dir / "wboxai_app"
            if wboxai_app_dir.is_dir():
                (wboxai_app_dir / ".env").write_text("\n".join(env_lines), encoding="utf-8")
                
            intro_val = self.config_data.get("intro_text", "").strip()
            if intro_val:
                (exe_dir / "intro_context.txt").write_text(intro_val, encoding="utf-8")
                if wboxai_app_dir.is_dir():
                    (wboxai_app_dir / "intro_context.txt").write_text(intro_val, encoding="utf-8")
                
            self.fin_desc.setText(
                "Configuration settings saved successfully!\n\n"
                "You can now launch the WboxAI application."
            )
            self.chk_launch.setText("Launch WboxAI now")
            self.pages.setCurrentIndex(5)
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Could not write configuration settings:\n{e}")

    def save_configuration_locally(self):
        try:
            frozen = getattr(sys, "frozen", False)
            exe_dir = Path(sys.executable).resolve().parent if frozen else Path(__file__).resolve().parent
            
            existing_env = {}
            env_file = exe_dir / ".env"
            if env_file.is_file():
                try:
                    from dotenv import dotenv_values
                    existing_env = dict(dotenv_values(env_file))
                except Exception:
                    pass

            updates = {
                "LIGHTWEIGHT_MODE": "true",
                "MAX_WORKERS": "1",
                "OPENAI_API_KEY": self.config_data.get("openai_key", ""),
                "GEMINI_API_KEY": self.config_data.get("gemini_key", ""),
                "CLAUDE_API_KEY": self.config_data.get("claude_key", ""),
                "JOB_ROLE": self.config_data.get("job_role", "Software Engineer"),
                "JOB_DESCRIPTION": self.config_data.get("job_desc", ""),
                "CODE_LANGUAGE": self.config_data.get("code_lang", "python"),
                "CODING_MODE": "auto",
                "AUDIO_SOURCE": "loopback",
                "ENTERPRISE_AUDIO": "true",
                "AUDIO_STT_PROVIDER": "speech_to_text",
                "SPEECH_TO_TEXT_SERVER_URL": "ws://127.0.0.1:8000",
                "SPEECH_TO_TEXT_PROVIDER": "deepgram",
                "SCREEN_WATCH_ENABLED": "false",
                "EMAIL_RECEIVER": self.config_data.get("email_recv", ""),
                "SMTP_SERVER": self.config_data.get("smtp_server", "smtp.gmail.com"),
                "SMTP_PORT": self.config_data.get("smtp_port", "587"),
                "SMTP_USERNAME": self.config_data.get("smtp_user", ""),
                "SMTP_PASSWORD": self.config_data.get("smtp_pass", ""),
                "SMTP_USE_TLS": "true",
            }

            for k, v in updates.items():
                if k not in existing_env or v:
                    existing_env[k] = v

            env_lines = ["# Created by WboxAI Setup Wizard"]
            for k, v in existing_env.items():
                env_lines.append(f"{k}={v}")

            env_file.write_text("\n".join(env_lines), encoding="utf-8")

            wboxai_app_dir = exe_dir / "wboxai_app"
            if wboxai_app_dir.is_dir():
                (wboxai_app_dir / ".env").write_text("\n".join(env_lines), encoding="utf-8")

            # Create default empty context files if they don't exist
            intro_val = self.config_data.get("intro_text", "").strip() or "Enter details about yourself for introductions."
            contexts = {
                "resume_context.txt": "Paste your resume plain text here.",
                "intro_context.txt": intro_val,
                "project_overview.txt": "Add details of major projects you worked on."
            }
            for name, content in contexts.items():
                p = exe_dir / name
                if name == "intro_context.txt" or not p.is_file():
                    p.write_text(content, encoding="utf-8")
                if wboxai_app_dir.is_dir():
                    p_wboxai = wboxai_app_dir / name
                    if name == "intro_context.txt" or not p_wboxai.is_file():
                        p_wboxai.write_text(content, encoding="utf-8")
            
            # Create shortcuts if Windows
            if sys.platform == "win32":
                self.create_windows_shortcuts(Path(sys.executable).resolve())
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Could not write configuration settings:\n{e}")

    def launch_app(self):
        try:
            frozen = getattr(sys, "frozen", False)
            if frozen:
                app_path = Path(self.edit_path.text().strip()) / "wboxai.exe"
                if app_path.is_file():
                    subprocess.Popen([str(app_path)])
            else:
                app_path = Path(__file__).resolve().parent / "main.py"
                python_exe = sys.executable
                subprocess.Popen([python_exe, str(app_path)])
        except Exception as launch_err:
            print(f"Failed to launch main app: {launch_err}")


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(THEME_CSS)
    
    config_only = "--config-only" in sys.argv
    
    wizard = SetupWizard(config_only=config_only)
    if config_only:
        wizard.pages.setCurrentIndex(6)
        wizard.update_navigation()
        
    wizard.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
