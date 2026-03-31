"""模型下載對話框"""

from __future__ import annotations

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

# 可下載的 ASR 模型清單
_ASR_MODELS = [
    "Qwen/Qwen3-ASR-0.6B",
    "Qwen/Qwen3-ASR-1.7B",
]


class _DownloadWorker(QThread):
    """在背景執行緒下載 Hugging Face 模型"""

    progress = Signal(str)   # 進度訊息
    finished = Signal(str)   # 完成，帶快取目錄路徑
    error = Signal(str)

    def __init__(self, model_id: str, local_only: bool = False):
        super().__init__()
        self.model_id = model_id
        self.local_only = local_only

    def run(self) -> None:
        try:
            from huggingface_hub import snapshot_download  # type: ignore

            self.progress.emit(f"開始下載 {self.model_id} …")

            local_dir = snapshot_download(
                repo_id=self.model_id,
                local_files_only=self.local_only,
            )
            self.finished.emit(local_dir)
        except Exception as e:  # noqa: BLE001
            self.error.emit(str(e))


class ModelDownloadDialog(QDialog):
    """模型下載 / 驗證對話框"""

    def __init__(self, parent=None, preset_model: str = ""):
        super().__init__(parent)
        self.setWindowTitle("下載 / 更新模型")
        self.resize(520, 400)
        self._worker: _DownloadWorker | None = None
        self._preset_model = preset_model
        self._setup_ui()

        # 若傳入預設模型，自動選取
        if preset_model and preset_model in _ASR_MODELS:
            self.model_combo.setCurrentText(preset_model)

    # ── UI 建構 ──────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # 模型選擇
        group = QGroupBox("ASR 模型")
        g_layout = QVBoxLayout(group)

        self.model_combo = QComboBox()
        for m in _ASR_MODELS:
            self.model_combo.addItem(m)
        g_layout.addWidget(self.model_combo)

        self.offline_check = QCheckBox("僅使用本機快取（不連網）")
        g_layout.addWidget(self.offline_check)

        layout.addWidget(group)

        # 進度
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)   # indeterminate
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("下載日誌將顯示在此處…")
        layout.addWidget(self.log_view)

        # 按鈕
        btn_layout = QDialogButtonBox()
        self.download_btn = QPushButton("⬇ 下載 / 驗證")
        self.download_btn.clicked.connect(self._on_download)
        btn_layout.addButton(self.download_btn, QDialogButtonBox.ButtonRole.ActionRole)

        close_btn = btn_layout.addButton(QDialogButtonBox.StandardButton.Close)
        close_btn.clicked.connect(self.accept)

        layout.addWidget(btn_layout)

    # ── 行為 ─────────────────────────────────────────────────────────────

    def _on_download(self) -> None:
        model_id = self.model_combo.currentText()
        local_only = self.offline_check.isChecked()

        if self._worker and self._worker.isRunning():
            self._log("⚠ 已有下載作業進行中，請稍候…")
            return

        self.download_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.log_view.clear()

        self._worker = _DownloadWorker(model_id, local_only)
        self._worker.progress.connect(self._log)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_finished(self, local_dir: str) -> None:
        self._log(f"✅ 下載完成！\n快取目錄：{local_dir}")
        self._reset_ui()

    def _on_error(self, err: str) -> None:
        self._log(f"❌ 下載失敗：{err}")
        self._reset_ui()

    def _log(self, msg: str) -> None:
        self.log_view.append(msg)

    def _reset_ui(self) -> None:
        self.progress_bar.setVisible(False)
        self.download_btn.setEnabled(True)

    def closeEvent(self, event) -> None:
        if self._worker and self._worker.isRunning():
            self._worker.terminate()
            self._worker.wait()
        event.accept()
