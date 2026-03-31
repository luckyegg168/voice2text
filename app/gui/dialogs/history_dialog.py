"""歷史紀錄對話框"""

import asyncio
from datetime import datetime

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.history_manager import get_history_manager


class _HistoryLoadWorker(QThread):
    done = Signal(list)
    error = Signal(str)

    def __init__(self, search: str = ""):
        super().__init__()
        self.search = search

    def run(self) -> None:
        try:
            mgr = get_history_manager()
            items, _ = asyncio.run(
                mgr.list(search=self.search if self.search else None, limit=100)
            )
            self.done.emit(items)
        except Exception as e:
            self.error.emit(str(e))


class _HistoryDeleteWorker(QThread):
    done = Signal(str)   # search text to reload with
    error = Signal(str)

    def __init__(self, item_id: str, search: str = ""):
        super().__init__()
        self.item_id = item_id
        self.search = search

    def run(self) -> None:
        try:
            mgr = get_history_manager()
            asyncio.run(mgr.delete(self.item_id))
            self.done.emit(self.search)
        except Exception as e:
            self.error.emit(str(e))


class HistoryDialog(QDialog):
    """歷史紀錄對話框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_items = []
        self.setWindowTitle("History")
        self.resize(600, 500)
        self._setup_ui()
        self._load_history()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_input)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)

        layout.addLayout(search_layout)
        layout.addWidget(self.list_widget)

        buttons_layout = QHBoxLayout()

        self.play_btn = QPushButton("▶ Play")
        self.play_btn.clicked.connect(self._on_play)
        buttons_layout.addWidget(self.play_btn)

        self.copy_btn = QPushButton("📋 Copy")
        self.copy_btn.clicked.connect(self._on_copy)
        buttons_layout.addWidget(self.copy_btn)

        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.clicked.connect(self._on_delete)
        buttons_layout.addWidget(self.delete_btn)

        buttons_layout.addStretch()

        close_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn.rejected.connect(self.accept)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

    def _load_history(self, search: str = "") -> None:
        self._load_worker = _HistoryLoadWorker(search)
        self._load_worker.done.connect(self._on_history_loaded)
        self._load_worker.error.connect(
            lambda e: self.list_widget.addItem(f"載入失敗: {e}")
        )
        self._load_worker.start()

    def _on_history_loaded(self, items: list) -> None:
        self.current_items = items
        self._populate_list(items)

    def _populate_list(self, items: list) -> None:
        self.list_widget.clear()
        for item in items:
            created = datetime.fromisoformat(item["created_at"])
            text_preview = item["text"][:80] + "..." if len(item["text"]) > 80 else item["text"]

            widget_item = QListWidgetItem(self.list_widget)
            widget = QWidget()
            layout = QVBoxLayout(widget)

            title = QLabel(f"[{item['id']}] {created.strftime('%Y-%m-%d %H:%M:%S')}")
            title.setStyleSheet("font-weight: bold;")
            layout.addWidget(title)

            preview = QLabel(text_preview)
            preview.setWordWrap(True)
            layout.addWidget(preview)

            info = QLabel(
                f"Lang: {item.get('language', 'N/A')} | "
                f"Model: {item.get('model', 'N/A')} | "
                f"Duration: {item.get('duration', 0):.1f}s"
            )
            info.setStyleSheet("color: #666; font-size: 9pt;")
            layout.addWidget(info)

            widget.setMinimumHeight(80)
            widget_item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(widget_item)

    def _on_search(self, text: str) -> None:
        self._load_history(search=text)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        index = self.list_widget.row(item)
        if 0 <= index < len(self.current_items):
            selected_item = self.current_items[index]
            self.parent().set_transcription_text(selected_item["text"])
            self.accept()

    def _on_play(self) -> None:
        pass

    def _on_copy(self) -> None:
        index = self.list_widget.currentRow()
        if 0 <= index < len(self.current_items):
            text = self.current_items[index]["text"]
            from PySide6.QtWidgets import QApplication

            QApplication.clipboard().setText(text)

    def _on_delete(self) -> None:
        index = self.list_widget.currentRow()
        if 0 <= index < len(self.current_items):
            item = self.current_items[index]
            search = self.search_input.text()
            self._delete_worker = _HistoryDeleteWorker(item["id"], search)
            self._delete_worker.done.connect(self._load_history)
            self._delete_worker.error.connect(
                lambda e: self.list_widget.addItem(f"刪除失敗: {e}")
            )
            self._delete_worker.start()
