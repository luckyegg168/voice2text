"""主視窗"""

import asyncio
import tempfile
from pathlib import Path

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from app.core import audio_processor, history_manager, qwen3_asr
from app.core.audio_processor import AudioProcessor
from app.core.config import get_settings
from app.core.opencc_engine import opencc_engine
from app.gui.dialogs import HistoryDialog, HotwordsDialog, SettingsDialog, TranslationDialog
from app.gui.utils.signal_bus import signal_bus
from app.gui.utils.theme import get_stylesheet
from app.gui.widgets import (
    AudioLevelIndicator,
    ControlPanel,
    StatusBar,
    TranscriptionArea,
)


class TranscriptionWorker(QThread):
    """轉寫工作執行緒"""

    finished = Signal(str, str)
    error = Signal(str)

    def __init__(self, audio_data, model_id: str, language: str):
        super().__init__()
        self.audio_data = audio_data
        self.model_id = model_id
        self.language = language

    def run(self) -> None:
        try:
            text, lang = qwen3_asr.transcribe(
                audio_input=self.audio_data,
                model_id=self.model_id,
                language=None if self.language == "auto" else self.language,
            )
            self.finished.emit(text, lang)
        except Exception as e:
            self.error.emit(str(e))


class RecordingWorker(QThread):
    """錄音工作執行緒"""

    level_changed = Signal(float)
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, duration: float = 30.0):
        super().__init__()
        self.duration = duration
        self._processor: AudioProcessor | None = None

    def run(self) -> None:
        try:
            self._processor = AudioProcessor()
            audio = self._processor.record(
                duration=self.duration,
                callback=lambda level: self.level_changed.emit(level),
            )
            self.finished.emit(audio)
        except Exception as e:
            self.error.emit(str(e))

    def stop(self) -> None:
        if self._processor is not None:
            self._processor.stop()


class MainWindow(QMainWindow):
    """主視窗"""

    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.recording_worker = None
        self.transcription_worker = None
        self.current_audio_data = None
        self.is_recording = False

        self.setWindowTitle("Voice2Text — 語音辨識工具")
        self.resize(920, 680)
        self.setMinimumSize(700, 520)
        self.setStyleSheet(get_stylesheet())

        self._setup_ui()
        self._setup_menu()
        self._connect_signals()
        self._setup_shortcuts()

        signal_bus.model_loaded.connect(self._on_model_loaded)

    def _setup_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        self.control_panel = ControlPanel()
        layout.addWidget(self.control_panel)

        self.transcription_area = TranscriptionArea()
        layout.addWidget(self.transcription_area, 1)

        self.audio_indicator = AudioLevelIndicator()
        layout.addWidget(self.audio_indicator)

        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)

    def _setup_menu(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu("檔案(&F)")

        open_action = file_menu.addAction("開啟音訊檔…")
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self._on_open)

        save_action = file_menu.addAction("儲存文字…")
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self._on_save)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("結束")
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)

        settings_menu = menubar.addMenu("設定(&S)")

        settings_action = settings_menu.addAction("偏好設定…")
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self._on_settings)

        history_action = settings_menu.addAction("歷史記錄…")
        history_action.setShortcut(QKeySequence("Ctrl+H"))
        history_action.triggered.connect(self._on_history)

        hotwords_action = settings_menu.addAction("熱詞管理…")
        hotwords_action.triggered.connect(self._on_hotwords)

        help_menu = menubar.addMenu("說明(&H)")

        about_action = help_menu.addAction("關於 Voice2Text")
        about_action.triggered.connect(self._on_about)

    def _connect_signals(self) -> None:
        self.control_panel.record_clicked.connect(self._on_record)
        self.control_panel.open_clicked.connect(self._on_open)
        self.control_panel.save_clicked.connect(self._on_save)
        self.control_panel.copy_clicked.connect(self._on_copy)
        self.control_panel.clear_clicked.connect(self._on_clear)
        self.control_panel.convert_clicked.connect(self._on_convert)
        self.control_panel.translate_clicked.connect(self._on_translate)

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self._on_record)
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self._on_open)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self._on_save)
        QShortcut(QKeySequence("Ctrl+Shift+C"), self).activated.connect(self._on_copy)
        QShortcut(QKeySequence("Escape"), self).activated.connect(self._stop_recording)

    def _on_record(self) -> None:
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self) -> None:
        self.is_recording = True
        self.control_panel.set_record_state(True)
        self.status_bar.set_recording(True)
        self.audio_indicator.reset()

        self.recording_worker = RecordingWorker(duration=30.0)
        self.recording_worker.level_changed.connect(
            lambda level: self.audio_indicator.set_level(level)
        )
        self.recording_worker.finished.connect(self._on_recording_finished)
        self.recording_worker.error.connect(self._on_recording_error)
        self.recording_worker.start()

    def _stop_recording(self) -> None:
        if self.recording_worker:
            self.recording_worker.stop()
            self.recording_worker = None

        self.is_recording = False
        self.control_panel.set_record_state(False)
        self.status_bar.set_recording(False)

    def _on_recording_finished(self, audio_data) -> None:
        self.current_audio_data = audio_data
        self._transcribe_audio(audio_data)

    def _on_recording_error(self, error: str) -> None:
        self.is_recording = False
        self.control_panel.set_record_state(False)
        self.status_bar.set_recording(False)
        self.status_bar.set_status("錄音失敗")
        QMessageBox.critical(self, "錄音錯誤", f"錄音發生錯誤：\n{error}")

    def _transcribe_audio(self, audio_data) -> None:
        model = self.control_panel.get_model()
        language = self.control_panel.get_language()

        self.status_bar.set_status("辨識中…")
        self.transcription_area.clear_text()
        self.transcription_area.append_text("辨識中，請稍候…")

        self.transcription_worker = TranscriptionWorker(
            audio_data=audio_data,
            model_id=model,
            language=language,
        )
        self.transcription_worker.finished.connect(self._on_transcription_finished)
        self.transcription_worker.error.connect(self._on_transcription_error)
        self.transcription_worker.start()

    def _on_transcription_finished(self, text: str, language: str) -> None:
        self.transcription_area.set_text(text)
        self.status_bar.set_status("就緒")

        if self.settings.vad_enabled and self.current_audio_data is not None:
            self._save_to_history(text, language)

    def _on_transcription_error(self, error: str) -> None:
        self.transcription_area.set_text(f"辨識失敗：{error}")
        self.status_bar.set_status("辨識失敗")
        QMessageBox.critical(self, "辨識錯誤", f"辨識發生錯誤：\n{error}")

    def _on_open(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Audio",
            "",
            "Audio Files (*.wav *.mp3 *.flac);;All Files (*)",
        )

        if file_path:
            try:
                data, sr = AudioProcessor.load_wav(file_path)
                audio_16k = AudioProcessor.convert_to_16kmono(data, sr)
                self.current_audio_data = audio_16k
                self._transcribe_audio(audio_16k)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{e}")

    def _on_save(self) -> None:
        text = self.transcription_area.get_text()
        if not text:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "儲存文字",
            "",
            "Text Files (*.txt);;All Files (*)",
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
                self.status_bar.set_status(f"已儲存至 {Path(file_path).name}")
            except Exception as e:
                QMessageBox.critical(self, "儲存失敗", f"儲存失敗：\n{e}")

    def _on_copy(self) -> None:
        text = self.transcription_area.get_text()
        if text:
            QApplication.clipboard().setText(text)
            self.status_bar.set_status("已複製到剪貼簿！")

    def _on_clear(self) -> None:
        self.transcription_area.clear_text()
        self.current_audio_data = None
        self.audio_indicator.reset()

    def _on_convert(self, mode: str) -> None:
        text = self.transcription_area.get_text()
        if text:
            converted = opencc_engine.convert(text, mode)
            self.transcription_area.set_text(converted)

    def _on_translate(self, target_lang: str) -> None:
        text = self.transcription_area.get_text()
        if not text:
            return

        dialog = TranslationDialog(text, self)
        dialog.exec()

    def _on_settings(self) -> None:
        dialog = SettingsDialog(self)
        dialog.exec()

    def _on_history(self) -> None:
        dialog = HistoryDialog(self)
        dialog.exec()

    def _on_hotwords(self) -> None:
        dialog = HotwordsDialog(self)
        dialog.exec()

    def _on_about(self) -> None:
        QMessageBox.about(
            self,
            "關於 Voice2Text",
            "<b>Voice2Text</b> v0.1.0<br><br>"
            "語音辨識轉文字工具<br><br>"
            "• Qwen3-ASR 語音辨識<br>"
            "• OpenCC 繁簡中文轉換<br>"
            "• 本地 LLM 翻譯<br><br>"
            "Ctrl+R 錄音 │ Ctrl+O 開啟 │ Ctrl+S 儲存<br>"
            "Ctrl+Shift+C 複製 │ Esc 停止錄音",
        )

    def _on_model_loaded(self, model_name: str) -> None:
        self.status_bar.set_model(model_name)

    def set_transcription_text(self, text: str) -> None:
        """設定轉寫文字（用於從歷史回填）"""
        self.transcription_area.set_text(text)

    def _save_to_history(self, text: str, language: str) -> None:
        """儲存到歷史紀錄"""
        asyncio.run(self._async_save_to_history(text, language))

    async def _async_save_to_history(self, text: str, language: str) -> None:
        model = self.control_panel.get_model()

        recordings_dir = self.settings.recordings_dir
        recordings_dir.mkdir(parents=True, exist_ok=True)

        timestamp = Path(tempfile.mktemp(suffix=".wav", dir=recordings_dir))
        AudioProcessor.save_wav(
            str(timestamp),
            self.current_audio_data,
            self.settings.sample_rate,
        )

        history_mgr = history_manager.get_history_manager()
        duration = len(self.current_audio_data) / self.settings.sample_rate

        await history_mgr.add(
            text=text,
            language=language,
            model=model,
            audio_path=str(timestamp),
            duration=duration,
        )

        signal_bus.history_updated.emit()

    def closeEvent(self, event) -> None:
        self._stop_recording()
        if self.transcription_worker and self.transcription_worker.isRunning():
            self.transcription_worker.wait()
        event.accept()
