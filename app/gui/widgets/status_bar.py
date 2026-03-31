"""狀態列元件"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget


class _DotIndicator(QLabel):
    """閃爍錄音指示燈"""

    _ON_CSS  = "color: #FF4757; font-size: 11pt;"
    _OFF_CSS = "color: #2E3347; font-size: 11pt;"

    def __init__(self, parent: QWidget = None):
        super().__init__("●", parent)
        self._blink = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._toggle)
        self.setFixedWidth(18)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(self._OFF_CSS)

    def start(self) -> None:
        self._blink = True
        self.setStyleSheet(self._ON_CSS)
        self._timer.start(600)

    def stop(self) -> None:
        self._timer.stop()
        self._blink = False
        self.setStyleSheet(self._OFF_CSS)

    def _toggle(self) -> None:
        self._blink = not self._blink
        self.setStyleSheet(self._ON_CSS if self._blink else self._OFF_CSS)


_CSS = "color: #8B90A0; font-size: 9pt;"


class StatusBar(QWidget):
    """底部狀態列（使用 setStatusBar 嵌入主視窗）"""

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMaximumHeight(28)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(10)

        self._dot = _DotIndicator()
        layout.addWidget(self._dot)

        self.status_label = QLabel("就緒")
        self.status_label.setStyleSheet(_CSS)
        layout.addWidget(self.status_label)

        layout.addStretch()

        self.model_label = QLabel("模型：—")
        self.model_label.setStyleSheet(_CSS)
        layout.addWidget(self.model_label)

        sep = QLabel("│")
        sep.setStyleSheet("color: #2E3347;")
        layout.addWidget(sep)

        self.memory_label = QLabel("記憶體：—")
        self.memory_label.setStyleSheet(_CSS)
        layout.addWidget(self.memory_label)

        sep2 = QLabel("│")
        sep2.setStyleSheet("color: #2E3347;")
        layout.addWidget(sep2)

        self.api_dot = QLabel("● API")
        self.api_dot.setStyleSheet("color: #8B90A0; font-size: 9pt;")
        self.api_dot.setToolTip("翻譯 API 狀態未知")
        layout.addWidget(self.api_dot)

    # ── 公開 API ──────────────────────────────────────────────────────────

    def set_status(self, status: str) -> None:
        self.status_label.setText(status)

    def set_model(self, model: str) -> None:
        self.model_label.setText(f"模型：{model}")

    def set_memory(self, memory: str) -> None:
        self.memory_label.setText(f"記憶體：{memory}")

    def set_api_status(self, ok: bool) -> None:
        if ok:
            self.api_dot.setStyleSheet("color: #00D4AA; font-size: 9pt;")
            self.api_dot.setToolTip("翻譯 API 已連線")
        else:
            self.api_dot.setStyleSheet("color: #FF4757; font-size: 9pt;")
            self.api_dot.setToolTip("翻譯 API 未連線")

    def set_recording(self, recording: bool) -> None:
        if recording:
            self._dot.start()
            self.set_status("錄音中…")
        else:
            self._dot.stop()
            self.set_status("就緒")
