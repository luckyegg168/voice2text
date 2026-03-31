"""轉寫文字區元件"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextOption
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class TranscriptionArea(QWidget):
    """帶字數統計的轉寫文字容器"""

    text_changed = Signal(str)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── 文字編輯區 ──
        self.editor = QTextEdit()
        self.editor.setReadOnly(False)
        self.editor.setPlaceholderText(
            "語音轉寫結果將顯示在這裡\n\n"
            "• 點擊「⏺ 開始錄音」錄製麥克風\n"
            "• 點擊「📂 開啟」載入音訊檔案\n"
            "• 文字可直接編輯、複製或儲存"
        )

        font = QFont("Segoe UI", 11)
        font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 101)
        self.editor.setFont(font)
        self.editor.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.editor.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.editor.setStyleSheet("""
            QTextEdit {
                background-color: #1A1D27;
                color: #E8EAF0;
                border: 1px solid #2E3347;
                border-radius: 8px;
                padding: 14px 16px;
                selection-background-color: #6C63FF;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border: 1.5px solid #6C63FF;
            }
        """)
        self.editor.textChanged.connect(self._on_text_changed)
        root.addWidget(self.editor, 1)

        # ── 字數列 ──
        footer = QHBoxLayout()
        footer.setContentsMargins(4, 4, 4, 0)

        self.char_label = QLabel("字元：0")
        self.char_label.setStyleSheet("color: #4A4F60; font-size: 8.5pt;")
        self.word_label = QLabel("字詞：0")
        self.word_label.setStyleSheet("color: #4A4F60; font-size: 8.5pt;")

        footer.addWidget(self.char_label)
        footer.addStretch()
        footer.addWidget(self.word_label)
        root.addLayout(footer)

    # ── private ──────────────────────────────────────────────────────────

    def _on_text_changed(self) -> None:
        text = self.editor.toPlainText()
        chars = len(text)
        words = len(text.split()) if text.strip() else 0
        self.char_label.setText(f"字元：{chars:,}")
        self.word_label.setText(f"字詞：{words:,}")
        self.text_changed.emit(text)

    # ── 公開 API ──────────────────────────────────────────────────────────

    def set_text(self, text: str) -> None:
        self.editor.setPlainText(text)

    def get_text(self) -> str:
        return self.editor.toPlainText()

    def append_text(self, text: str) -> None:
        self.editor.append(text)

    def clear_text(self) -> None:
        self.editor.clear()
