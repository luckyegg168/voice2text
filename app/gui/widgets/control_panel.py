"""控制面板元件"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.core.constants import SUPPORTED_LANGUAGES


def _v_sep() -> QFrame:
    """建立垂直分隔線"""
    line = QFrame()
    line.setFrameShape(QFrame.Shape.VLine)
    line.setFrameShadow(QFrame.Shadow.Plain)
    line.setStyleSheet("color: #2E3347;")
    line.setFixedWidth(1)
    return line


class ControlPanel(QWidget):
    """現代化控制面板"""

    record_clicked = Signal()
    open_clicked = Signal()
    save_clicked = Signal()
    copy_clicked = Signal()
    clear_clicked = Signal()
    convert_clicked = Signal(str)
    translate_clicked = Signal(str)
    download_model_clicked = Signal(str)   # 傳遞選中的 model_id

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._recording = False
        self._setup_ui()

    # ── 內部樣式 ──────────────────────────────────────────────────────────

    _PANEL_CSS = """
        ControlPanel {
            background-color: #1A1D27;
            border: 1px solid #2E3347;
            border-radius: 10px;
        }
    """
    _SECTION_CSS = "font-size: 8pt; font-weight: 600; color: #8B90A0; letter-spacing: 0.5px;"

    # ── UI 建構 ───────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self.setStyleSheet(self._PANEL_CSS)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 10, 14, 10)
        root.setSpacing(8)

        root.addLayout(self._build_top_row())
        root.addLayout(self._build_action_row())

    def _build_top_row(self) -> QHBoxLayout:
        """模型 + 語言 + 翻譯目標"""
        row = QHBoxLayout()
        row.setSpacing(12)

        # ── 模型選擇 ──
        model_lbl = QLabel("MODEL")
        model_lbl.setStyleSheet(self._SECTION_CSS)
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Qwen3-ASR-0.6B", "Qwen3-ASR-1.7B"])
        self.model_combo.setToolTip("選擇 ASR 語音辨識模型\n0.6B 速度快；1.7B 精度高")
        self.model_combo.setFixedWidth(170)

        self.download_btn = QPushButton("⬇")
        self.download_btn.setObjectName("downloadButton")
        self.download_btn.setToolTip("下載 / 更新選取的 ASR 模型")
        self.download_btn.setFixedSize(30, 30)
        self.download_btn.clicked.connect(
            lambda: self.download_model_clicked.emit(self.get_model())
        )

        row.addWidget(model_lbl)
        row.addWidget(self.model_combo)
        row.addWidget(self.download_btn)
        row.addWidget(_v_sep())

        # ── 語言選擇 ──
        lang_lbl = QLabel("LANGUAGE")
        lang_lbl.setStyleSheet(self._SECTION_CSS)
        self.language_combo = QComboBox()
        self.language_combo.addItems(SUPPORTED_LANGUAGES)
        self.language_combo.setToolTip("選擇音訊語言（auto 為自動偵測）")
        self.language_combo.setFixedWidth(130)

        row.addWidget(lang_lbl)
        row.addWidget(self.language_combo)
        row.addWidget(_v_sep())

        # ── 翻譯目標 ──
        trans_lbl = QLabel("TRANSLATE TO")
        trans_lbl.setStyleSheet(self._SECTION_CSS)
        self.translate_combo = QComboBox()
        self.translate_combo.addItems(["中文", "英文", "日文", "韓文", "法文", "德文"])
        self.translate_combo.setFixedWidth(100)

        row.addWidget(trans_lbl)
        row.addWidget(self.translate_combo)

        row.addStretch()
        return row

    def _build_action_row(self) -> QHBoxLayout:
        """主要操作按鈕列"""
        row = QHBoxLayout()
        row.setSpacing(8)

        # 錄音（主按鈕，大）
        self.record_btn = QPushButton("⏺  開始錄音")
        self.record_btn.setObjectName("recordButton")
        self.record_btn.setToolTip("開始 / 停止錄音  (Ctrl+R)")
        self.record_btn.setFixedWidth(165)
        self.record_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.record_btn.clicked.connect(self.record_clicked.emit)
        row.addWidget(self.record_btn)

        row.addWidget(_v_sep())

        # 次要按鈕
        btns = [
            ("open_btn",    "📂  開啟",  "開啟音訊檔案  (Ctrl+O)", self.open_clicked.emit),
            ("save_btn",    "💾  儲存",  "儲存文字  (Ctrl+S)",    self.save_clicked.emit),
            ("copy_btn",    "⎘  複製",  "複製全部文字  (Ctrl+C)", self.copy_clicked.emit),
        ]
        for attr, label, tip, slot in btns:
            btn = QPushButton(label)
            btn.setToolTip(tip)
            btn.clicked.connect(slot)
            setattr(self, attr, btn)
            row.addWidget(btn)

        row.addWidget(_v_sep())

        # 轉換 / 翻譯
        self.convert_btn = QPushButton("⇄  簡繁")
        self.convert_btn.setToolTip("簡繁中文互換")
        self.convert_btn.clicked.connect(lambda: self.convert_clicked.emit("s2t"))
        row.addWidget(self.convert_btn)

        self.translate_btn = QPushButton("🌐  翻譯")
        self.translate_btn.setObjectName("primaryButton")
        self.translate_btn.setToolTip("使用 LLM 翻譯文字")
        self.translate_btn.clicked.connect(
            lambda: self.translate_clicked.emit(self.translate_combo.currentText())
        )
        row.addWidget(self.translate_btn)

        row.addWidget(_v_sep())

        # 清除
        self.clear_btn = QPushButton("✕  清除")
        self.clear_btn.setToolTip("清除所有文字")
        self.clear_btn.clicked.connect(self.clear_clicked.emit)
        row.addWidget(self.clear_btn)

        row.addStretch()
        return row

    # ── 公開 API ──────────────────────────────────────────────────────────

    def get_model(self) -> str:
        idx = self.model_combo.currentIndex()
        return ["Qwen/Qwen3-ASR-0.6B", "Qwen/Qwen3-ASR-1.7B"][idx]

    def get_language(self) -> str:
        return self.language_combo.currentText()

    def set_record_state(self, recording: bool) -> None:
        self._recording = recording
        if recording:
            self.record_btn.setText("⏹  停止錄音")
            self.record_btn.setProperty("recording", "true")
        else:
            self.record_btn.setText("⏺  開始錄音")
            self.record_btn.setProperty("recording", "false")
        # 觸發 QSS 重新套用
        self.record_btn.style().unpolish(self.record_btn)
        self.record_btn.style().polish(self.record_btn)
