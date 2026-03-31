"""翻譯對話框"""

import asyncio

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from app.core.translation_service import get_translation_service


class TranslationWorker(QThread):
    """翻譯工作執行緒"""

    finished = Signal(str)
    error = Signal(str)

    def __init__(self, text: str, target_lang: str, source_lang: str = None):
        super().__init__()
        self.text = text
        self.target_lang = target_lang
        self.source_lang = source_lang

    def run(self) -> None:
        try:
            service = get_translation_service()
            result = asyncio.run(
                service.translate(
                    text=self.text,
                    target_language=self.target_lang,
                    source_language=self.source_lang,
                )
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class TranslationDialog(QDialog):
    """翻譯對話框"""

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.source_text = text
        self.worker = None
        self.setWindowTitle("Translation")
        self.resize(500, 400)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Source Text:"))
        self.source_text_edit = QTextEdit()
        self.source_text_edit.setPlainText(self.source_text)
        self.source_text_edit.setReadOnly(True)
        layout.addWidget(self.source_text_edit)

        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Target Language:"))

        self.target_combo = QComboBox()
        self.target_combo.addItems(
            ["中文", "英文", "日文", "韓文", "法文", "德文", "西班牙文", "葡萄牙文"]
        )
        lang_layout.addWidget(self.target_combo)

        self.translate_btn = QPushButton("🔊 Translate")
        self.translate_btn.clicked.connect(self._on_translate)
        lang_layout.addWidget(self.translate_btn)

        lang_layout.addStretch()
        layout.addLayout(lang_layout)

        layout.addWidget(QLabel("Translation Result:"))
        self.result_edit = QTextEdit()
        self.result_edit.setReadOnly(True)
        layout.addWidget(self.result_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Copy | QDialogButtonBox.StandardButton.Close
        )
        buttons.button(QDialogButtonBox.StandardButton.Copy).clicked.connect(self._on_copy)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)

    def _on_translate(self) -> None:
        self.translate_btn.setEnabled(False)
        self.result_edit.setPlainText("Translating...")

        self.worker = TranslationWorker(
            text=self.source_text,
            target_lang=self.target_combo.currentText(),
        )
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_finished(self, result: str) -> None:
        self.result_edit.setPlainText(result)
        self.translate_btn.setEnabled(True)

    def _on_error(self, error: str) -> None:
        self.result_edit.setPlainText(f"Error: {error}")
        self.translate_btn.setEnabled(True)

    def _on_copy(self) -> None:
        from PySide6.QtWidgets import QApplication

        QApplication.clipboard().setText(self.result_edit.toPlainText())
