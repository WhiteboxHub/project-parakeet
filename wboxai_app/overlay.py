"""Overlay UI — invisible in screen share (Windows + macOS)."""

from __future__ import annotations

from PyQt6.QtCore import (
    QEasingCurve,
    QEvent,
    QPoint,
    QPropertyAnimation,
    QRect,
    Qt,
    QTimer,
    pyqtProperty,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QAction,
    QActionGroup,
    QBrush,
    QColor,
    QFont,
    QGuiApplication,
    QIcon,
    QKeySequence,
    QMouseEvent,
    QPainter,
    QPalette,
    QPen,
    QShortcut,
    QWheelEvent,
)
from PyQt6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPlainTextEdit,
    QPushButton,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

import config
from capture_exclude import apply_to_window
from glass_effect import apply_glass_backdrop
from glass_theme import stylesheet as glass_stylesheet
from llm_project.response_parser import ParsedResponse

_DRAG_STRIP_H = 28
_RESIZE_GRIP = 22


class _DragStrip(QWidget):
    """Top bar — drag to move (visible + hit-testable on Windows)."""

    def __init__(self, window: QMainWindow):
        super().__init__()
        self._window = window
        self._offset: QPoint | None = None
        self.setObjectName("drag_strip")
        self.setFixedHeight(_DRAG_STRIP_H)
        self.setToolTip("Drag here to move the window")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        grip = QLabel("⋮⋮⋮  drag to move")
        grip.setObjectName("drag_grip")
        grip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Let the strip receive presses made directly on the label text.
        grip.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        row = QVBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(grip)

    def paintEvent(self, event) -> None:
        from PyQt6.QtWidgets import QStyleOption, QStyle
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)

        # Fully transparent pixels can be click-through on Windows layered
        # windows. Alpha 1 is invisible but keeps the whole strip hit-testable.
        alpha = (
            1
            if config.GLASS_SEE_THROUGH and config.GLASS_PANEL_TINT_PERCENT <= 1
            else 12
        )
        painter.fillRect(self.rect(), QColor(255, 255, 255, alpha))
        painter.end()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._offset = event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()
            handle = self._window.windowHandle()
            if handle is not None and handle.startSystemMove():
                self._offset = None
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self._window.move(event.globalPosition().toPoint() - self._offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._offset = None
        super().mouseReleaseEvent(event)


class QToggleSwitch(QAbstractButton):
    def __init__(self, parent=None, text=""):
        super().__init__(parent)
        self.setText(text)
        self.setCheckable(True)
        self.setSizePolicy(self.sizePolicy().Policy.Fixed, self.sizePolicy().Policy.Fixed)
        self._thumb_position = 3.0
        self._animation = QPropertyAnimation(self, b"thumb_position", self)
        self._animation.setDuration(120)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self._height = 24
        self._width = max(64, len(text) * 8 + 32) if text else 46
        self.setFixedSize(self._width, self._height)
        
    @pyqtProperty(float)
    def thumb_position(self) -> float:
        return self._thumb_position
        
    @thumb_position.setter
    def thumb_position(self, pos: float) -> None:
        self._thumb_position = pos
        self.update()
        
    def nextCheckState(self) -> None:
        super().nextCheckState()
        start = self._thumb_position
        end = float(self.width() - self.height() + 3.0) if self.isChecked() else 3.0
        self._animation.stop()
        self._animation.setStartValue(start)
        self._animation.setEndValue(end)
        self._animation.start()
        
    def setChecked(self, checked: bool) -> None:
        super().setChecked(checked)
        self._animation.stop()
        self._thumb_position = float(self.width() - self.height() + 3.0) if checked else 3.0
        self.update()
        
    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Colors: checked track uses Premium Blue, unchecked uses frosted transparent gray
        bg_checked = QColor(59, 130, 246, 220)  # Premium Blue
        bg_unchecked = QColor(255, 255, 255, 60)  # Frosted transparent gray
        thumb_color = QColor(255, 255, 255)
        
        rect = self.rect()
        radius = rect.height() / 2.0
        
        # Draw background track
        p.setPen(Qt.PenStyle.NoPen)
        bg = bg_checked if self.isChecked() else bg_unchecked
        p.setBrush(QBrush(bg))
        p.drawRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), radius, radius)
        
        # Draw text inside track if present
        if self.text():
            p.setPen(QColor(255, 255, 255, 220) if self.isChecked() else QColor(255, 255, 255, 140))
            font = QFont("Segoe UI" if config.IS_WINDOWS else ".AppleSystemUIFont", 8, QFont.Weight.Bold)
            p.setFont(font)
            if self.isChecked():
                # Thumb is on the right, draw text on the left
                text_rect = QRect(4, 0, self.width() - self.height(), self.height())
                p.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.text())
            else:
                # Thumb is on the left, draw text on the right
                text_rect = QRect(self.height() - 4, 0, self.width() - self.height(), self.height())
                p.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.text())
        
        # Draw thumb handle
        thumb_diameter = rect.height() - 6.0
        p.setBrush(QBrush(thumb_color))
        p.drawEllipse(int(self._thumb_position), 3, int(thumb_diameter), int(thumb_diameter))
        p.end()


class _ResizeGrip(QWidget):
    """Bottom-right corner — drag to resize."""

    def __init__(self, window: QMainWindow):
        super().__init__()
        self._window = window
        self._origin: QPoint | None = None
        self._start_size: QPoint | None = None
        self.setObjectName("resize_grip")
        self.setFixedSize(_RESIZE_GRIP, _RESIZE_GRIP)
        self.setToolTip("Drag to resize window")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(255, 255, 255, 40))
        painter.setPen(QColor(255, 255, 255, 220))
        w, h = self.width(), self.height()
        for i in range(3):
            o = 4 + i * 5
            painter.drawLine(w - o, h - 4, w - 4, h - o)
        painter.end()
        super().paintEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._origin = event.globalPosition().toPoint()
            self._start_size = QPoint(self._window.width(), self._window.height())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if (
            self._origin is not None
            and self._start_size is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            delta = event.globalPosition().toPoint() - self._origin
            w = max(self._window.minimumWidth(), self._start_size.x() + delta.x())
            h = max(self._window.minimumHeight(), self._start_size.y() + delta.y())
            self._window.resize(w, h)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._origin = None
        self._start_size = None
        super().mouseReleaseEvent(event)


def get_candidate_list() -> list[dict]:
    import urllib.request
    import json
    import config

    # Base mock candidates
    mocks = [
        {
            "name": "Jashuva",
            "role": "AI Engineer",
            "resume": {
                "name": "Jashuva",
                "skills": ["Python", "Generative AI", "LangGraph", "Milvus", "Redis", "AWS Bedrock", "MCP Servers"],
                "experience": [
                    {
                        "role": "AI Engineer",
                        "project": "Agentic AI Platform Migration",
                        "summary": "Modernized Enterprise RAG platform to Agentic AI utilizing LangGraph and Milvus vector db."
                    }
                ]
            }
        },
        {
            "name": "Alice Smith",
            "role": "Senior Cloud Solutions Architect",
            "resume": {
                "name": "Alice Smith",
                "skills": ["AWS", "GCP", "Terraform", "Kubernetes", "Python", "Docker"],
                "experience": [
                    {
                        "role": "Solutions Architect",
                        "project": "Microservices Migration",
                        "summary": "Led infrastructure automation using Terraform and migrated legacy monoliths to Kubernetes clusters."
                    }
                ]
            }
        },
        {
            "name": "Bob Johnson",
            "role": "Full Stack Engineer",
            "resume": {
                "name": "Bob Johnson",
                "skills": ["React", "Node.js", "PostgreSQL", "Redis", "TypeScript", "Docker"],
                "experience": [
                    {
                        "role": "Full Stack Developer",
                        "project": "Real-time Analytics Dashboard",
                        "summary": "Designed secure GraphQL APIs and optimized PostgreSQL database query execution time by 40%."
                    }
                ]
            }
        }
    ]

    if not config.CANDIDATE_API_URL:
        return mocks

    try:
        req = urllib.request.Request(config.CANDIDATE_API_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode('utf-8'))
            if isinstance(data, list):
                res_list = []
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    item_copy = dict(item)
                    if "name" not in item_copy:
                        item_copy["name"] = "Unknown"
                    if "role" not in item_copy:
                        item_copy["role"] = "Software Engineer"
                    if "resume" not in item_copy:
                        item_copy["resume"] = item_copy.copy()
                    res_list.append(item_copy)
                return res_list + mocks
            elif isinstance(data, dict) and "candidates" in data:
                res = data["candidates"]
                if isinstance(res, list):
                    res_list = []
                    for item in res:
                        if not isinstance(item, dict):
                            continue
                        item_copy = dict(item)
                        if "name" not in item_copy:
                            item_copy["name"] = "Unknown"
                        if "role" not in item_copy:
                            item_copy["role"] = "Software Engineer"
                        if "resume" not in item_copy:
                            item_copy["resume"] = item_copy.copy()
                        res_list.append(item_copy)
                    return res_list + mocks
    except Exception as e:
        print(f"[Candidates API] Failed to fetch from {config.CANDIDATE_API_URL}: {e}")
    
    return mocks


def show_resume_dialog(parent=None) -> None:
    from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QMessageBox, QLabel, QComboBox
    from PyQt6.QtCore import Qt
    import json
    import time
    import config

    dialog = QDialog(parent)
    dialog.setWindowTitle("Select Candidate for Interview Session")
    dialog.setMinimumSize(500, 420)
    dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)

    layout = QVBoxLayout(dialog)

    # Candidate drop-down selection
    lbl_select = QLabel("Select Candidate:")
    layout.addWidget(lbl_select)

    combo_candidates = QComboBox()
    
    # Load candidate list (API + mocks)
    candidates = get_candidate_list()
    for idx, cand in enumerate(candidates):
        combo_candidates.addItem(f"{cand['name']} ({cand['role']})", idx)
    layout.addWidget(combo_candidates)

    lbl_preview = QLabel("Resume Details Preview (JSON):")
    layout.addWidget(lbl_preview)

    text_preview = QTextEdit()
    layout.addWidget(text_preview)

    # Update preview helper
    def update_preview(index):
        if 0 <= index < len(candidates):
            cand = candidates[index]
            resume_data = cand.get("resume", cand)
            text_preview.setPlainText(json.dumps(resume_data, indent=2))

    combo_candidates.currentIndexChanged.connect(update_preview)
    # Trigger initial update
    if candidates:
        update_preview(0)

    btn_layout = QHBoxLayout()
    btn_start = QPushButton("Start WboxAI with Selected Candidate")
    btn_manual = QPushButton("Switch to Manual Edit")
    btn_layout.addWidget(btn_start)
    btn_layout.addWidget(btn_manual)
    layout.addLayout(btn_layout)

    # Manual edit mode switch
    def switch_to_manual():
        text_preview.setReadOnly(False)
        combo_candidates.setEnabled(False)
        btn_start.setText("Save & Start WboxAI")
        btn_manual.setEnabled(False)
        QMessageBox.information(dialog, "Manual Mode", "You can now edit or paste any JSON resume directly in the text preview box.")

    btn_manual.clicked.connect(switch_to_manual)

    text_preview.setReadOnly(True) # read-only until manual switch clicked

    def on_start():
        content = text_preview.toPlainText().strip()
        if not content:
            QMessageBox.warning(dialog, "Empty Resume", "Resume content is empty.")
            return

        try:
            parsed = json.loads(content)
            formatted = json.dumps(parsed, indent=2)
            config.RESUME_PATH.write_text(formatted, encoding="utf-8")
            
            # Save candidate name and timestamp state
            if combo_candidates.isEnabled():
                idx = combo_candidates.currentIndex()
                config.SELECTED_CANDIDATE_NAME = candidates[idx]["name"]
            else:
                config.SELECTED_CANDIDATE_NAME = parsed.get("name", "ManualCandidate")
                
            config.SESSION_TIMESTAMP = time.strftime("%Y%m%d_%H%M%S")
            print(f"[config] Selected candidate: '{config.SELECTED_CANDIDATE_NAME}' at {config.SESSION_TIMESTAMP}", flush=True)
            dialog.accept()
        except json.JSONDecodeError as jde:
            QMessageBox.critical(dialog, "Invalid JSON", f"Format error in JSON:\n{jde}")

    btn_start.clicked.connect(on_start)
    dialog.exec()


class OverlayWindow(QMainWindow):
    answer_ready = pyqtSignal(object)
    status_changed = pyqtSignal(str)
    listening_toggled = pyqtSignal(bool)
    force_coding_requested = pyqtSignal()
    scan_screen_requested = pyqtSignal()
    watch_screen_toggled = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._listening = False
        self._coding_visible = False
        self._last_question = ""
        self._transparent = config.use_transparent_overlay()
        self._share_hide_ok = False
        self._applying_exclude = False
        self._glass_applied = False
        self._layout_mode = "normal"
        self._saved_normal_geometry: QRect | None = None
        self._code_box_max_default = 200
        self.setMouseTracking(True)
        self._resize_dir = None
        self._resize_start_pos = None
        self._resize_start_geom = None
        self._setup_ui()
        self.installEventFilter(self)
        self.answer_ready.connect(self._set_response)

        self._exclude_debounce = QTimer(self)
        self._exclude_debounce.setSingleShot(True)
        self._exclude_debounce.timeout.connect(self._apply_exclude_once)

        if config.EXCLUDE_REFRESH_SEC > 0:
            self._exclude_slow = QTimer(self)
            self._exclude_slow.timeout.connect(self._apply_exclude_once)
            self._exclude_slow.start(config.EXCLUDE_REFRESH_SEC * 1000)

        self._contrast_timer = QTimer(self)
        self._contrast_timer.timeout.connect(self._check_screen_contrast)
        self._contrast_timer.start(2000)

    def _setup_ui(self) -> None:
        self.setWindowTitle("WboxAI")
        
        # Load window icon
        import sys
        from pathlib import Path
        frozen = getattr(sys, "frozen", False)
        if frozen:
            logo_path = Path(sys._MEIPASS) / "wboxai_app" / "logo.png"
        else:
            logo_path = Path(__file__).resolve().parent / "logo.png"
        if logo_path.is_file():
            self.setWindowIcon(QIcon(str(logo_path)))
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        if config.STEALTH_FOCUS:
            flags = flags | Qt.WindowType.WindowDoesNotAcceptFocus
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setWindowFlags(flags)
        if self._transparent:
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        else:
            self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        active_cnt = len(config.get_active_providers())
        min_w = 420 if active_cnt <= 1 else (650 if active_cnt == 2 else 900)
        self.setMinimumSize(min_w, 320)

        default_w = 680 if active_cnt <= 1 else (950 if active_cnt == 2 else 1200)
        self.resize(default_w, 520)

        central = QWidget()
        central.setObjectName("panel")
        if self._transparent:
            central.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            central.setAutoFillBackground(False)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        self._drag_strip = _DragStrip(self)
        if self._transparent:
            self._drag_strip.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        layout.addWidget(self._drag_strip)

        header = QHBoxLayout()
        title = QLabel("WboxAI")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()

        self.btn_coding = QToggleSwitch(text="Coding")
        self.btn_coding.setChecked(False)
        self.btn_coding.toggled.connect(self._on_force_coding_click)
        header.addWidget(self.btn_coding)

        self.btn_scan = QPushButton("Scan screen")
        self.btn_scan.setObjectName("primary")
        self.btn_scan.clicked.connect(self._on_scan_button_clicked)
        header.addWidget(self.btn_scan)

        self.btn_auto_scan = QToggleSwitch(text="Auto")
        self.btn_auto_scan.setChecked(False)
        self.btn_auto_scan.toggled.connect(self._on_auto_scan_toggled)
        header.addWidget(self.btn_auto_scan)

        self.btn_share_hide = QToggleSwitch(text="Share-Hide")
        self.btn_share_hide.setChecked(config.INVISIBLE_IN_SHARE)
        self.btn_share_hide.toggled.connect(self._on_share_hide_toggle)
        header.addWidget(self.btn_share_hide)

        self.btn_listen = QPushButton("Start listening")
        self.btn_listen.setObjectName("primary")
        self.btn_listen.clicked.connect(self._on_listen_click)
        header.addWidget(self.btn_listen)

        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("close")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setToolTip("Exit WboxAI")
        self.btn_close.clicked.connect(self._exit_app)
        header.addWidget(self.btn_close)

        layout.addLayout(header)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status")
        layout.addWidget(self.status_label)

        layout.addWidget(QLabel("Question / problem", objectName="section"))
        self.question_box = QTextEdit()
        self.question_box.setReadOnly(True)
        self.question_box.setMaximumHeight(72)
        self._make_see_through_edit(self.question_box)
        layout.addWidget(self.question_box)

        self.providers_layout = QHBoxLayout()
        layout.addLayout(self.providers_layout, stretch=1)

        self.columns = {}
        active = config.get_active_providers()
        if not active:
            no_key_lbl = QLabel(
                "Please configure at least one API key (OPENAI_API_KEY, GEMINI_API_KEY, or CLAUDE_API_KEY) in .env to use the copilot."
            )
            no_key_lbl.setWordWrap(True)
            no_key_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.providers_layout.addWidget(no_key_lbl)
        else:
            for provider in active:
                col_widget = QWidget()
                col_layout = QVBoxLayout(col_widget)
                col_layout.setContentsMargins(0, 0, 0, 0)
                col_layout.setSpacing(8)

                header_lbl = QLabel(f"{provider.capitalize()} Answer", objectName="section")
                col_layout.addWidget(header_lbl)

                answer_box = QTextEdit()
                answer_box.setReadOnly(True)
                self._make_see_through_edit(answer_box)
                col_layout.addWidget(answer_box, stretch=1)

                code_sec = QWidget()
                self._make_translucent_widget(code_sec)
                code_layout = QVBoxLayout(code_sec)
                code_layout.setContentsMargins(0, 0, 0, 0)

                code_header = QHBoxLayout()
                code_header.addWidget(QLabel("Code", objectName="section"))
                code_header.addStretch()

                btn_copy = QPushButton("Copy code")
                btn_copy.setObjectName("primary")
                code_header.addWidget(btn_copy)
                code_layout.addLayout(code_header)

                code_box = QPlainTextEdit()
                code_box.setReadOnly(True)
                self._make_see_through_edit(code_box)
                mono = QFont("Menlo" if config.IS_MAC else "Consolas", 16)
                code_box.setFont(mono)
                code_box.setMaximumHeight(200)
                code_layout.addWidget(code_box)

                col_layout.addWidget(code_sec)
                code_sec.hide()

                # Save references before connecting
                self.columns[provider] = {
                    "widget": col_widget,
                    "header": header_lbl,
                    "answer_box": answer_box,
                    "code_section": code_sec,
                    "code_box": code_box,
                    "btn_copy": btn_copy
                }

                # Bind the specific code_box to copy function
                btn_copy.clicked.connect(lambda checked, cb=code_box: self._on_copy_provider_code(cb))

                self.providers_layout.addWidget(col_widget)

        hint = QLabel("Hover + scroll here · drag top bar to move · Ctrl+H hide")
        hint.setObjectName("hint")
        layout.addWidget(hint)

        resize_row = QHBoxLayout()
        resize_row.setContentsMargins(0, 0, 0, 0)
        resize_row.addStretch()
        self._resize_grip = _ResizeGrip(self)
        resize_row.addWidget(self._resize_grip)
        layout.addLayout(resize_row)

        self.setCentralWidget(central)
        self._central_panel = central
        self._install_edge_filters(central)
        if config.STEALTH_FOCUS:
            self._apply_stealth_focus(central)

        see_through = config.GLASS_SEE_THROUGH and self._transparent
        if see_through:
            widgets = [
                self.findChild(QLabel, "title"),
                self.status_label,
                self.findChild(QLabel, "hint"),
                self.question_box,
            ]
            for col in self.columns.values():
                widgets.append(col["header"])
                widgets.append(col["answer_box"])
                widgets.append(col["code_box"])
            for w in widgets:
                if w is not None:
                    self._apply_text_halo(w)
            for w in central.findChildren(QLabel, "section"):
                self._apply_text_halo(w)
        elif self._transparent:
            widgets = [
                self.findChild(QLabel, "title"),
                self.status_label,
                self.findChild(QLabel, "hint"),
            ]
            for col in self.columns.values():
                widgets.append(col["header"])
            for w in widgets:
                if w is not None:
                    self._apply_text_halo(w)
            for w in central.findChildren(QLabel, "section"):
                self._apply_text_halo(w)
        else:
            self._apply_panel_shadow(central)
        self.setStyleSheet(glass_stylesheet(transparent=self._transparent))
        QApplication.setFont(QFont("Segoe UI" if config.IS_WINDOWS else ".AppleSystemUIFont", 14))

        QShortcut(QKeySequence("Ctrl+H"), self, self.hide)
        QShortcut(QKeySequence("Ctrl+Shift+H"), self, self._show_and_exclude)
        QShortcut(QKeySequence("Ctrl+Shift+C"), self, self._shortcut_force_coding)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self._on_scan_button_clicked)
        QShortcut(QKeySequence("Escape"), self, self._exit_app)

    def _make_translucent_widget(self, widget: QWidget) -> None:
        if self._transparent:
            widget.setAutoFillBackground(False)

    def _make_see_through_edit(self, edit: QTextEdit | QPlainTextEdit) -> None:
        """Force text areas transparent with a strong text outline/halo so it works on any background."""
        self._make_translucent_widget(edit)
        pal = edit.palette()
        pal.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0, 1))
        pal.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        edit.setPalette(pal)
        edit.setStyleSheet(
            "background: rgba(0, 0, 0, 1); background-color: rgba(0, 0, 0, 1); border: none; color: #FFFFFF;"
        )
        self._apply_text_halo(edit)

    def _apply_stealth_focus(self, central: QWidget) -> None:
        """Hover + wheel scroll without focusing the overlay (keeps coding tab active)."""
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        central.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        boxes = [self.question_box]
        for col in self.columns.values():
            boxes.append(col["answer_box"])
            boxes.append(col["code_box"])

        for box in boxes:
            box.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            box.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        buttons = [
            self.btn_coding,
            self.btn_scan,
            self.btn_auto_scan,
            self.btn_share_hide,
            self.btn_listen,
            self.btn_close,
        ] + [col["btn_copy"] for col in self.columns.values()]

        for btn in buttons:
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def _scroll_target_at(self, global_pos: QPoint) -> QTextEdit | QPlainTextEdit | None:
        panel = getattr(self, "_central_panel", None)
        if panel is None:
            return None
        local = panel.mapFromGlobal(global_pos)
        
        # 1. Check if inside the question box area
        if self.question_box.geometry().contains(local):
            return self.question_box

        # 2. Check if inside any provider column area
        for provider, col in self.columns.items():
            if col["widget"].geometry().contains(local):
                col_local = col["widget"].mapFrom(panel, local)
                if col["code_section"].isVisible() and col_local.y() > col["widget"].height() * 0.45:
                    return col["code_box"]
                return col["answer_box"]

        # 3. Fallback: if hovering over the overlay window itself (margins, spacing, drag-strip)
        if self.rect().contains(self.mapFromGlobal(global_pos)):
            if self.columns:
                primary = "openai" if "openai" in self.columns else list(self.columns.keys())[0]
                return self.columns[primary]["answer_box"]
            return self.question_box

        return None

    @staticmethod
    def _apply_wheel_scroll(target: QTextEdit | QPlainTextEdit, delta_y: int) -> None:
        bar = target.verticalScrollBar()
        step = max(20, abs(delta_y) // 3)
        bar.setValue(bar.value() - step if delta_y > 0 else bar.value() + step)

    @staticmethod
    def _apply_text_halo(widget: QWidget) -> None:
        """Strong black shadow/halo so white copilot text stays readable on any background."""
        fx = QGraphicsDropShadowEffect(widget)
        fx.setBlurRadius(8)
        fx.setOffset(0, 0)
        fx.setColor(QColor(0, 0, 0, 255))
        widget.setGraphicsEffect(fx)

    @staticmethod
    def _apply_panel_shadow(panel: QWidget) -> None:
        fx = QGraphicsDropShadowEffect(panel)
        fx.setBlurRadius(28)
        fx.setOffset(0, 6)
        fx.setColor(QColor(0, 0, 0, 70))
        panel.setGraphicsEffect(fx)

    def _apply_glass_backdrop(self) -> None:
        if not self._transparent or self._glass_applied:
            return
        if config.GLASS_BLUR_PERCENT <= 0:
            return
        if apply_glass_backdrop(self, config.GLASS_BLUR_PERCENT):
            self._glass_applied = True

    def _install_edge_filters(self, root: QWidget) -> None:
        root.installEventFilter(self)
        for child in root.findChildren(QWidget):
            child.installEventFilter(self)

    def _apply_stealth_win32(self) -> None:
        if not config.STEALTH_FOCUS or not config.IS_WINDOWS:
            return
        try:
            from win_stealth import prevent_activation_steal

            handle = self.windowHandle()
            hwnd = int(handle.winId()) if handle is not None else int(self.winId())
            prevent_activation_steal(hwnd)
        except Exception:
            pass

    def eventFilter(self, obj, event) -> bool:
        et = event.type()

        if et == QEvent.Type.Wheel and isinstance(event, QWheelEvent):
            target = self._scroll_target_at(event.globalPosition().toPoint())
            if target is not None:
                self._apply_wheel_scroll(target, event.angleDelta().y())
                event.accept()
                return True
            return False

        return False

    def wheelEvent(self, event: QWheelEvent) -> None:
        target = self._scroll_target_at(event.globalPosition().toPoint())
        if target is not None:
            self._apply_wheel_scroll(target, event.angleDelta().y())
            event.accept()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            border = 8
            w = self.width()
            h = self.height()

            left = pos.x() < border
            right = pos.x() > w - border
            top = pos.y() < border
            bottom = pos.y() > h - border

            direction = ""
            if left: direction += "L"
            if right: direction += "R"
            if top: direction += "T"
            if bottom: direction += "B"

            if direction:
                self._resize_dir = direction
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_geom = self.geometry()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        pos = event.position().toPoint()
        border = 8
        w = self.width()
        h = self.height()

        if not event.buttons() & Qt.MouseButton.LeftButton:
            left = pos.x() < border
            right = pos.x() > w - border
            top = pos.y() < border
            bottom = pos.y() > h - border

            if (left and top) or (right and bottom):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif (right and top) or (left and bottom):
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            elif left or right:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif top or bottom:
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        elif self._resize_dir:
            delta = event.globalPosition().toPoint() - self._resize_start_pos
            geom = QRect(self._resize_start_geom)
            min_w = self.minimumWidth()
            min_h = self.minimumHeight()

            if "L" in self._resize_dir:
                new_w = max(min_w, geom.width() - delta.x())
                geom.setLeft(geom.right() - new_w + 1)
            if "R" in self._resize_dir:
                new_w = max(min_w, geom.width() + delta.x())
                geom.setWidth(new_w)
            if "T" in self._resize_dir:
                new_h = max(min_h, geom.height() - delta.y())
                geom.setTop(geom.bottom() - new_h + 1)
            if "B" in self._resize_dir:
                new_h = max(min_h, geom.height() + delta.y())
                geom.setHeight(new_h)

            self.setGeometry(geom)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._resize_dir = None
        self._resize_start_pos = None
        self._resize_start_geom = None
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.schedule_exclude()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.schedule_exclude()
        QTimer.singleShot(80, self._apply_glass_backdrop)
        if config.STEALTH_FOCUS:
            QTimer.singleShot(100, self._apply_stealth_win32)

    def show(self) -> None:
        super().show()
        self.raise_()
        if not config.STEALTH_FOCUS:
            self.activateWindow()
        self.schedule_exclude()

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        if event.type() in (QEvent.Type.WindowActivate, QEvent.Type.Show):
            self.schedule_exclude()

    def schedule_exclude(self) -> None:
        """Debounced — avoids freezing UI on Windows."""
        self._exclude_debounce.start(200)

    def _apply_exclude_once(self) -> None:
        if not config.INVISIBLE_IN_SHARE or self._applying_exclude:
            return
        self._applying_exclude = True
        try:
            ok, note = apply_to_window(self)
            self._share_hide_ok = ok
            if note and not ok:
                self.status_label.setText(note)
        finally:
            self._applying_exclude = False

    def _show_and_exclude(self) -> None:
        self.show()
        self._apply_exclude_once()

    def hide_for_screenshot(self) -> None:
        self.hide()

    def restore_after_screenshot(self) -> None:
        self.show()
        QTimer.singleShot(100, self._apply_exclude_once)

    def _exit_app(self) -> None:
        app = QApplication.instance()
        if app is not None:
            app.quit()
        else:
            self.close()

    def _on_configure_clicked(self) -> None:
        from installer import SetupWizard
        
        # Temporarily enable focus on main window so setup wizard works perfectly
        old_flags = self.windowFlags()
        if config.STEALTH_FOCUS:
            self.setWindowFlags(old_flags & ~Qt.WindowType.WindowDoesNotAcceptFocus)
            self.show()
            
        self.wizard = SetupWizard(config_only=True)
        self.wizard.setWindowFlags(self.wizard.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        def on_wizard_closed():
            if config.STEALTH_FOCUS:
                self.setWindowFlags(old_flags)
                self.show()
            self.schedule_exclude()
            
        self.wizard.closed.connect(on_wizard_closed)
        self.wizard.show()

    def _on_listen_click(self) -> None:
        self._listening = not self._listening
        self.btn_listen.setText("Stop listening" if self._listening else "Start listening")
        self.listening_toggled.emit(self._listening)
        self.schedule_exclude()

    def _on_force_coding_click(self, *args) -> None:
        self.force_coding_requested.emit()
        self.schedule_exclude()

    def set_coding_busy(self, busy: bool) -> None:
        self.btn_coding.setEnabled(not busy)

    def _on_scan_button_clicked(self) -> None:
        self.scan_screen_requested.emit()
        self.schedule_exclude()

    def _on_auto_scan_toggled(self, checked: bool) -> None:
        self.watch_screen_toggled.emit(checked)
        self.schedule_exclude()

    def _on_share_hide_toggle(self, checked: bool) -> None:
        config.INVISIBLE_IN_SHARE = checked
        if checked:
            ok, note = apply_to_window(self)
            self._share_hide_ok = ok
            if note:
                self.status_label.setText(note)
        else:
            from capture_exclude import restore_window
            ok, note = restore_window(self)
            if note:
                self.status_label.setText(note)
        self.schedule_exclude()

    def _on_copy_provider_code(self, code_box) -> None:
        code = code_box.toPlainText().strip()
        if code:
            QGuiApplication.clipboard().setText(code)
            self.status_label.setText("Code copied")
        self.schedule_exclude()

    def _shortcut_force_coding(self) -> None:
        self.btn_coding.setChecked(not self.btn_coding.isChecked())

    def set_listening_state(self, listening: bool) -> None:
        self._listening = listening
        self.btn_listen.setText("Stop listening" if listening else "Start listening")

    def apply_coding_layout(self) -> None:
        """Tall strip on the left — room for approach + code top to bottom."""
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        avail = screen.availableGeometry()
        if self._layout_mode != "coding":
            self._saved_normal_geometry = self.geometry()
        self._layout_mode = "coding"
        margin = 10
        
        num_cols = len(self.columns)
        if num_cols == 3:
            width = min(1200, max(900, int(avail.width() * 0.6)))
        elif num_cols == 2:
            width = min(900, max(680, int(avail.width() * 0.45)))
        else:
            width = min(500, max(360, int(avail.width() * 0.34)))

        self.setGeometry(
            avail.x() + margin,
            avail.y() + margin,
            width,
            avail.height() - 2 * margin,
        )
        self.question_box.setMaximumHeight(56)
        for col in self.columns.values():
            col["code_box"].setMaximumHeight(16_777_215)

    def apply_normal_layout(self) -> None:
        """Restore compact window after behavioral / non-coding answers."""
        if self._layout_mode == "coding":
            if self._saved_normal_geometry is not None:
                self.setGeometry(self._saved_normal_geometry)
            else:
                num_cols = len(self.columns)
                normal_w = 680 if num_cols <= 1 else (950 if num_cols == 2 else 1200)
                self.resize(normal_w, 520)
                self.move(80, 80)
        self._layout_mode = "normal"
        self.question_box.setMaximumHeight(72)
        for col in self.columns.values():
            col["code_box"].setMaximumHeight(self._code_box_max_default)

    def _set_response(self, data: dict) -> None:
        if not isinstance(data, dict):
            return
        provider = data.get("provider")
        response = data.get("response")
        if provider not in self.columns:
            return

        col = self.columns[provider]
        if (response.is_coding or response.code) and self.btn_coding.isChecked():
            col["code_section"].show()
            col["header"].setText(f"{provider.capitalize()} (Approach)")
            col["answer_box"].setPlainText(response.approach or response.full_text)
            col["code_box"].setPlainText(response.code)
            self.apply_coding_layout()
        else:
            col["code_section"].hide()
            col["header"].setText(f"{provider.capitalize()} Answer")
            full_content = response.approach or response.full_text
            if response.code and not self.btn_coding.isChecked():
                if "```" not in full_content:
                    full_content += f"\n\nCode:\n```{config.CODE_LANGUAGE}\n{response.code}\n```"
            col["answer_box"].setPlainText(full_content)
            self.btn_coding.setChecked(False)
            self.apply_normal_layout()
        self.schedule_exclude()

    def set_watch_checked(self, checked: bool) -> None:
        self.btn_auto_scan.setChecked(checked)

    def set_question(self, text: str) -> None:
        self._last_question = text
        self.question_box.setPlainText(text)

    def get_last_question(self) -> str:
        return self._last_question

    def _check_screen_contrast(self) -> None:
        """Lightweight background contrast sampler that updates text color mode dynamically."""
        try:
            screen = QGuiApplication.primaryScreen()
            if not screen:
                return

            geom = self.geometry()
            pixmap = screen.grabWindow(0, geom.x(), geom.y(), geom.width(), geom.height())
            image = pixmap.toImage()

            brightness_sum = 0.0
            count = 0
            step_x = max(1, geom.width() // 10)
            step_y = max(1, geom.height() // 10)
            for x in range(0, geom.width(), step_x):
                for y in range(0, geom.height(), step_y):
                    color = image.pixelColor(x, y)
                    luminance = 0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()
                    brightness_sum += luminance
                    count += 1

            if count > 0:
                avg = brightness_sum / count
                self.set_text_color_mode(is_light_bg=(avg > 140))
        except Exception:
            pass

    def set_text_color_mode(self, is_light_bg: bool) -> None:
        """Dynamically update the text color and black/white shadow outlines."""
        color_str = "#000000" if is_light_bg else "#FFFFFF"
        shadow_color = QColor(255, 255, 255, 255) if is_light_bg else QColor(0, 0, 0, 255)

        boxes = [self.question_box]
        for col in self.columns.values():
            boxes.append(col["answer_box"])
            boxes.append(col["code_box"])

        for box in boxes:
            box.setStyleSheet(
                f"background: transparent; background-color: transparent; border: none; color: {color_str};"
            )
            fx = box.graphicsEffect()
            if isinstance(fx, QGraphicsDropShadowEffect):
                fx.setColor(shadow_color)

        label_style = f"background: transparent; color: {color_str};"
        for lbl in self.findChildren(QLabel):
            if lbl.objectName() in ("title", "section", "hint") or isinstance(lbl, QLabel):
                lbl.setStyleSheet(label_style)
                fx = lbl.graphicsEffect()
                if isinstance(fx, QGraphicsDropShadowEffect):
                    fx.setColor(shadow_color)

    # Back-compat for main.py
    def ensure_invisible_to_share(self) -> None:
        self.schedule_exclude()
