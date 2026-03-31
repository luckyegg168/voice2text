"""主題樣式 — 現代深色介面"""

# ── 調色盤 ────────────────────────────────────────────────────────────────
COLORS = {
    # 背景層次
    "bg_base":     "#0F1117",   # 最深底層
    "bg_surface":  "#1A1D27",   # 卡片/面板
    "bg_elevated": "#222636",   # 懸浮元素

    # 強調色
    "primary":     "#6C63FF",   # 主紫色
    "primary_dim": "#4A43CC",
    "primary_glow":"#6C63FF33",

    # 狀態色
    "accent_green": "#00D4AA",   # 就緒 / 成功
    "accent_red":   "#FF4757",   # 錄音中 / 錯誤
    "accent_amber": "#FFB400",   # 警告

    # 文字
    "text_primary":   "#E8EAF0",
    "text_secondary":  "#8B90A0",
    "text_disabled":   "#4A4F60",

    # 邊框
    "border":       "#2E3347",
    "border_focus": "#6C63FF",
}

# ── 全域樣式表 ────────────────────────────────────────────────────────────
def get_stylesheet() -> str:
    """回傳完整 QSS 樣式表"""
    c = COLORS
    return f"""
/* ── Base ── */
QMainWindow, QWidget {{
    background-color: {c['bg_base']};
    color: {c['text_primary']};
    font-family: 'Segoe UI', 'Microsoft JhengHei UI', 'PingFang TC', sans-serif;
    font-size: 10pt;
}}

/* ── MenuBar ── */
QMenuBar {{
    background-color: {c['bg_surface']};
    border-bottom: 1px solid {c['border']};
    padding: 2px 0;
    spacing: 0;
}}
QMenuBar::item {{
    padding: 5px 12px;
    border-radius: 4px;
    margin: 2px 2px;
    color: {c['text_secondary']};
}}
QMenuBar::item:selected {{
    background-color: {c['primary_glow']};
    color: {c['text_primary']};
}}
QMenuBar::item:pressed {{
    background-color: {c['primary']};
    color: white;
}}

/* ── Menu ── */
QMenu {{
    background-color: {c['bg_elevated']};
    border: 1px solid {c['border']};
    border-radius: 8px;
    padding: 4px;
}}
QMenu::item {{
    padding: 7px 20px 7px 12px;
    border-radius: 4px;
    color: {c['text_primary']};
}}
QMenu::item:selected {{
    background-color: {c['primary_glow']};
    color: {c['primary']};
}}
QMenu::separator {{
    height: 1px;
    background-color: {c['border']};
    margin: 4px 0;
}}

/* ── Buttons ── */
QPushButton {{
    background-color: {c['bg_elevated']};
    color: {c['text_primary']};
    border: 1px solid {c['border']};
    border-radius: 7px;
    padding: 8px 18px;
    min-width: 72px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {c['primary_glow']};
    border-color: {c['primary']};
    color: {c['primary']};
}}
QPushButton:pressed {{
    background-color: {c['primary_dim']};
    border-color: {c['primary_dim']};
    color: white;
}}
QPushButton:disabled {{
    background-color: {c['bg_surface']};
    color: {c['text_disabled']};
    border-color: {c['border']};
}}

/* 錄音主按鈕 */
QPushButton#recordButton {{
    background-color: {c['accent_green']};
    color: {c['bg_base']};
    border: none;
    font-size: 11pt;
    font-weight: 700;
    padding: 10px 28px;
    border-radius: 8px;
    min-width: 130px;
}}
QPushButton#recordButton:hover {{
    background-color: #00FFD0;
}}
QPushButton#recordButton:pressed {{
    background-color: #00A882;
}}
QPushButton#recordButton[recording="true"] {{
    background-color: {c['accent_red']};
    color: white;
}}
QPushButton#recordButton[recording="true"]:hover {{
    background-color: #FF6B78;
}}

/* 主要行動按鈕 */
QPushButton#primaryButton {{
    background-color: {c['primary']};
    color: white;
    border: none;
    font-weight: 600;
}}
QPushButton#primaryButton:hover {{
    background-color: #8078FF;
    color: white;
    border: none;
}}
QPushButton#primaryButton:pressed {{
    background-color: {c['primary_dim']};
    color: white;
}}

/* 下載按鈕（緊湊圖示）*/
QPushButton#downloadButton {{
    background-color: {c['bg_elevated']};
    color: {c['text_secondary']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    padding: 0px;
    min-width: 30px;
    font-size: 13pt;
}}
QPushButton#downloadButton:hover {{
    background-color: {c['primary_glow']};
    border-color: {c['primary']};
    color: {c['primary']};
}}

/* ── Input Fields ── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {c['bg_surface']};
    color: {c['text_primary']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    padding: 7px 10px;
    selection-background-color: {c['primary']};
    selection-color: white;
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1.5px solid {c['border_focus']};
    background-color: {c['bg_elevated']};
}}
QLineEdit::placeholder, QTextEdit::placeholder {{
    color: {c['text_disabled']};
}}

/* ── ComboBox ── */
QComboBox {{
    background-color: {c['bg_surface']};
    color: {c['text_primary']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    padding: 6px 10px;
    min-width: 100px;
}}
QComboBox:focus {{
    border: 1.5px solid {c['border_focus']};
}}
QComboBox:hover {{
    border-color: {c['primary']};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox::down-arrow {{
    width: 10px;
    height: 10px;
}}
QComboBox QAbstractItemView {{
    background-color: {c['bg_elevated']};
    color: {c['text_primary']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    selection-background-color: {c['primary_glow']};
    selection-color: {c['primary']};
    padding: 4px;
}}

/* ── Label ── */
QLabel {{
    color: {c['text_primary']};
    background: transparent;
}}
QLabel#appTitle {{
    font-size: 18pt;
    font-weight: 700;
    color: {c['primary']};
    letter-spacing: 1px;
}}
QLabel#subtitle {{
    font-size: 9pt;
    color: {c['text_secondary']};
}}
QLabel#sectionLabel {{
    font-size: 8.5pt;
    font-weight: 600;
    color: {c['text_secondary']};
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}
QLabel#statusOk {{
    color: {c['accent_green']};
    font-weight: 600;
}}
QLabel#statusError {{
    color: {c['accent_red']};
    font-weight: 600;
}}

/* ── ProgressBar (audio level) ── */
QProgressBar {{
    border: none;
    border-radius: 3px;
    background-color: {c['bg_elevated']};
    max-height: 6px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: {c['accent_green']};
    border-radius: 3px;
}}
QProgressBar[level="high"]::chunk {{
    background-color: {c['accent_red']};
}}
QProgressBar[level="mid"]::chunk {{
    background-color: {c['accent_amber']};
}}

/* ── GroupBox ── */
QGroupBox {{
    background-color: {c['bg_surface']};
    border: 1px solid {c['border']};
    border-radius: 8px;
    margin-top: 12px;
    padding: 16px 12px 10px 12px;
    font-weight: 600;
    color: {c['text_secondary']};
    font-size: 9pt;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {c['text_secondary']};
    background-color: {c['bg_surface']};
}}

/* ── TabWidget ── */
QTabWidget::pane {{
    border: 1px solid {c['border']};
    border-radius: 8px;
    background-color: {c['bg_surface']};
    top: -1px;
}}
QTabBar::tab {{
    background-color: transparent;
    color: {c['text_secondary']};
    border: none;
    border-bottom: 2px solid transparent;
    padding: 8px 20px;
    margin-right: 4px;
    font-weight: 500;
}}
QTabBar::tab:selected {{
    color: {c['primary']};
    border-bottom: 2px solid {c['primary']};
    font-weight: 600;
}}
QTabBar::tab:hover:!selected {{
    color: {c['text_primary']};
    background-color: {c['bg_elevated']};
    border-radius: 6px 6px 0 0;
}}

/* ── ListWidget ── */
QListWidget {{
    background-color: {c['bg_surface']};
    border: 1px solid {c['border']};
    border-radius: 8px;
    padding: 4px;
    outline: none;
}}
QListWidget::item {{
    padding: 8px;
    border-radius: 5px;
    color: {c['text_primary']};
}}
QListWidget::item:selected {{
    background-color: {c['primary_glow']};
    color: {c['primary']};
    border: 1px solid {c['primary']};
}}
QListWidget::item:hover:!selected {{
    background-color: {c['bg_elevated']};
}}

/* ── ScrollBar ── */
QScrollBar:vertical {{
    background: {c['bg_surface']};
    width: 8px;
    border-radius: 4px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {c['border']};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {c['text_secondary']};
}}
QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {c['bg_surface']};
    height: 8px;
    border-radius: 4px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {c['border']};
    border-radius: 4px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {c['text_secondary']};
}}

/* ── StatusBar ── */
QStatusBar {{
    background-color: {c['bg_surface']};
    border-top: 1px solid {c['border']};
    color: {c['text_secondary']};
    font-size: 9pt;
}}
QStatusBar::item {{
    border: none;
}}

/* ── Dialog ── */
QDialog {{
    background-color: {c['bg_base']};
}}

/* ── Splitter ── */
QSplitter::handle {{
    background-color: {c['border']};
}}

/* ── ToolTip ── */
QToolTip {{
    background-color: {c['bg_elevated']};
    color: {c['text_primary']};
    border: 1px solid {c['border']};
    border-radius: 5px;
    padding: 5px 8px;
    font-size: 9pt;
}}

/* ── CheckBox ── */
QCheckBox {{
    color: {c['text_primary']};
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1.5px solid {c['border']};
    background-color: {c['bg_surface']};
}}
QCheckBox::indicator:checked {{
    background-color: {c['primary']};
    border-color: {c['primary']};
}}
QCheckBox::indicator:hover {{
    border-color: {c['primary']};
}}

/* ── DialogButtonBox ── */
QDialogButtonBox QPushButton {{
    min-width: 80px;
}}

/* ── FormLayout labels ── */
QFormLayout QLabel {{
    color: {c['text_secondary']};
    font-size: 9.5pt;
}}
    """

