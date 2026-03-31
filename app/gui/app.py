"""GUI 應用程式進入點"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.core.config import get_settings
from app.gui.main_window import MainWindow
from app.gui.utils.theme import get_stylesheet


def main() -> None:
    """主程式"""
    settings = get_settings()
    settings.ensure_directories()

    QApplication.setStyle("Fusion")

    app = QApplication(sys.argv)
    app.setStyleSheet(get_stylesheet())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
