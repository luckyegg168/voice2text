"""設定對話框"""

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.config import get_settings


class SettingsDialog(QDialog):
    """設定對話框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = get_settings()
        self.setWindowTitle("Settings")
        self.resize(500, 400)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        tabs = QTabWidget()
        tabs.addTab(self._create_model_tab(), "Model")
        tabs.addTab(self._create_audio_tab(), "Audio")
        tabs.addTab(self._create_api_tab(), "API")
        tabs.addTab(self._create_gui_tab(), "GUI")

        layout.addWidget(tabs)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save_settings)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def _create_model_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group = QGroupBox("Model Settings")
        form = QFormLayout(group)

        self.model_combo = QComboBox()
        self.model_combo.addItems(["Qwen/Qwen3-ASR-0.6B", "Qwen/Qwen3-ASR-1.7B"])
        self.model_combo.setCurrentText(self.settings.default_model)
        form.addRow("Default Model:", self.model_combo)

        self.device_combo = QComboBox()
        self.device_combo.addItems(["cuda", "cpu"])
        self.device_combo.setCurrentText(self.settings.device)
        form.addRow("Device:", self.device_combo)

        self.dtype_combo = QComboBox()
        self.dtype_combo.addItems(["float16", "bfloat16", "float32"])
        self.dtype_combo.setCurrentText(self.settings.dtype)
        form.addRow("Dtype:", self.dtype_combo)

        layout.addWidget(group)
        layout.addStretch()
        return widget

    def _create_audio_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group = QGroupBox("Audio Settings")
        form = QFormLayout(group)

        self.sample_rate_edit = QLineEdit(str(self.settings.sample_rate))
        form.addRow("Sample Rate:", self.sample_rate_edit)

        self.channels_edit = QLineEdit(str(self.settings.channels))
        form.addRow("Channels:", self.channels_edit)

        self.vad_checkbox = QPushButton("Enable VAD")
        self.vad_checkbox.setCheckable(True)
        self.vad_checkbox.setChecked(self.settings.vad_enabled)
        form.addRow("VAD:", self.vad_checkbox)

        layout.addWidget(group)
        layout.addStretch()
        return widget

    def _create_api_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group = QGroupBox("Translation API")
        form = QFormLayout(group)

        self.api_url_edit = QLineEdit(self.settings.translation_api_url)
        form.addRow("API URL:", self.api_url_edit)

        self.api_key_edit = QLineEdit(self.settings.translation_api_key)
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("API Key:", self.api_key_edit)

        self.api_model_edit = QLineEdit(self.settings.translation_model)
        form.addRow("Model:", self.api_model_edit)

        layout.addWidget(group)

        group2 = QGroupBox("OpenCC")
        form2 = QFormLayout(group2)

        self.opencc_mode_combo = QComboBox()
        self.opencc_mode_combo.addItems(["s2t", "t2s", "s2tw", "tw2s", "s2hk", "hk2s"])
        self.opencc_mode_combo.setCurrentText(self.settings.opencc_mode)
        form2.addRow("Default Mode:", self.opencc_mode_combo)

        layout.addWidget(group2)
        layout.addStretch()
        return widget

    def _create_gui_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group = QGroupBox("GUI Settings")
        form = QFormLayout(group)

        self.gui_lang_combo = QComboBox()
        self.gui_lang_combo.addItems(["zh-TW", "en-US"])
        self.gui_lang_combo.setCurrentText(self.settings.gui_language)
        form.addRow("Language:", self.gui_lang_combo)

        layout.addWidget(group)
        layout.addStretch()
        return widget

    def _save_settings(self) -> None:
        self.settings.default_model = self.model_combo.currentText()
        self.settings.device = self.device_combo.currentText()
        self.settings.dtype = self.dtype_combo.currentText()
        self.settings.sample_rate = int(self.sample_rate_edit.text())
        self.settings.channels = int(self.channels_edit.text())
        self.settings.vad_enabled = self.vad_checkbox.isChecked()
        self.settings.translation_api_url = self.api_url_edit.text()
        self.settings.translation_api_key = self.api_key_edit.text()
        self.settings.translation_model = self.api_model_edit.text()
        self.settings.opencc_mode = self.opencc_mode_combo.currentText()
        self.settings.gui_language = self.gui_lang_combo.currentText()

        self.settings.save_settings()
        self.accept()

    def save_settings(self) -> None:
        """儲存設定到 .env"""
        env_path = self.settings.env_file
        if env_path and hasattr(self.settings, "model_config"):
            pass
