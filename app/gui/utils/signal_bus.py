"""信號匯流排 - 跨元件通訊"""

from PySide6.QtCore import QObject, Signal


class SignalBus(QObject):
    """信號匯流排"""

    transcription_started = Signal()
    transcription_completed = Signal(str, str)
    transcription_error = Signal(str)

    model_loading = Signal(str)
    model_loaded = Signal(str)
    model_unloaded = Signal()

    recording_started = Signal()
    recording_stopped = Signal()
    audio_level_changed = Signal(float)

    history_updated = Signal()
    settings_changed = Signal(dict)

    translation_started = Signal()
    translation_completed = Signal(str)
    translation_error = Signal(str)


signal_bus = SignalBus()
