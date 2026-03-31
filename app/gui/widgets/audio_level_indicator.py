"""多段 VU 音量計指示器"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

_SEGMENTS = 24          # 總段數
_GREEN_END = 16         # 綠色段上限
_AMBER_END = 21         # 黃色段上限（之後為紅色）

_COL_GREEN = "#00D4AA"
_COL_AMBER = "#FFB400"
_COL_RED   = "#FF4757"
_COL_OFF   = "#1E2130"


class _VUMeter(QWidget):
    """水平多段 VU 計 (自訂繪製)"""

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._value = 0          # 0 ~ _SEGMENTS
        self._peak  = 0
        self._peak_decay = 0
        self.setMinimumHeight(12)
        self.setMaximumHeight(14)

    def set_value(self, v: int) -> None:
        self._value = max(0, min(v, _SEGMENTS))
        if v >= self._peak:
            self._peak = v
            self._peak_decay = 0
        else:
            self._peak_decay += 1
            if self._peak_decay > 8:
                self._peak = max(self._peak - 1, v)
        self.update()

    def reset(self) -> None:
        self._value = 0
        self._peak  = 0
        self._peak_decay = 0
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        seg_w = (w - _SEGMENTS + 1) / _SEGMENTS
        gap   = 1.5

        for i in range(_SEGMENTS):
            x = i * (seg_w + gap)
            rect_args = (int(x), 0, max(int(seg_w), 2), h)

            if i < self._value:
                if i < _GREEN_END:
                    col = _COL_GREEN
                elif i < _AMBER_END:
                    col = _COL_AMBER
                else:
                    col = _COL_RED
            elif i == self._peak and self._peak > 0:
                col = _COL_AMBER
            else:
                col = _COL_OFF

            painter.fillRect(*rect_args, QColor(col))

        painter.end()


class AudioLevelIndicator(QWidget):
    """VU 音量計 + 標籤包裝"""

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._max_level = 0.0
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(8)

        lbl = QLabel("音量")
        lbl.setStyleSheet("color: #4A4F60; font-size: 8pt;")
        lbl.setFixedWidth(28)
        layout.addWidget(lbl)

        self._meter = _VUMeter()
        layout.addWidget(self._meter, 1)

    def set_level(self, level: float) -> None:
        """level: 0.0 ~ 1.0 (RMS or peak)"""
        self._max_level = max(self._max_level * 0.97, level)
        seg = int(min(level * _SEGMENTS, _SEGMENTS))
        self._meter.set_value(seg)

    def reset(self) -> None:
        self._max_level = 0.0
        self._meter.reset()

