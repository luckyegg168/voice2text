"""熱詞設定對話框"""

from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from app.core.hot_words import get_hotwords_manager


class HotwordsDialog(QDialog):
    """熱詞設定對話框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hotwords_manager = get_hotwords_manager()
        self.current_words = []
        self.current_group = None
        self.setWindowTitle("Hot Words Settings")
        self.resize(600, 400)
        self._setup_ui()
        self._load_groups()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)

        left_panel = QVBoxLayout()
        self.group_list = QListWidget()
        self.group_list.setMaximumWidth(150)
        self.group_list.itemClicked.connect(self._on_group_clicked)
        left_panel.addWidget(QLabel("Groups:"))
        left_panel.addWidget(self.group_list)

        group_buttons = QHBoxLayout()
        self.add_group_btn = QPushButton("+")
        self.add_group_btn.clicked.connect(self._on_add_group)
        self.remove_group_btn = QPushButton("-")
        self.remove_group_btn.clicked.connect(self._on_remove_group)
        group_buttons.addWidget(self.add_group_btn)
        group_buttons.addWidget(self.remove_group_btn)
        left_panel.addLayout(group_buttons)

        layout.addLayout(left_panel)

        right_panel = QVBoxLayout()

        right_panel.addWidget(QLabel("Words:"))
        self.word_list = QListWidget()
        self.word_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        right_panel.addWidget(self.word_list)

        word_form = QGroupBox("Add/Edit Word")
        form_layout = QFormLayout(word_form)

        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Enter word...")
        form_layout.addRow("Word:", self.word_input)

        weight_layout = QHBoxLayout()
        self.weight_slider = QSlider(Qt.Orientation.Horizontal)
        self.weight_slider.setRange(1, 30)
        self.weight_slider.setValue(10)
        self.weight_label = QLabel("1.0")
        self.weight_slider.valueChanged.connect(
            lambda v: self.weight_label.setText(f"{v / 10:.1f}")
        )
        weight_layout.addWidget(self.weight_slider)
        weight_layout.addWidget(self.weight_label)
        form_layout.addRow("Weight:", weight_layout)

        word_buttons = QHBoxLayout()
        self.add_word_btn = QPushButton("Add")
        self.add_word_btn.clicked.connect(self._on_add_word)
        self.remove_word_btn = QPushButton("Remove")
        self.remove_word_btn.clicked.connect(self._on_remove_word)
        word_buttons.addWidget(self.add_word_btn)
        word_buttons.addWidget(self.remove_word_btn)
        form_layout.addRow("", word_buttons)

        right_panel.addWidget(word_form)

        close_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn.rejected.connect(self.accept)
        right_panel.addWidget(close_btn)

        layout.addLayout(right_panel)

    def _load_groups(self) -> None:
        self.group_list.clear()
        groups = self.hotwords_manager.get_groups()

        for group in groups:
            self.group_list.addItem(group)

        if groups:
            self.group_list.setCurrentRow(0)
            self._on_group_clicked(self.group_list.item(0))

    def _on_group_clicked(self, item) -> None:
        self.current_group = item.text()
        self._load_words()

    def _load_words(self) -> None:
        self.word_list.clear()
        if not self.current_group:
            return

        self.current_words = self.hotwords_manager.get_words(self.current_group)
        for word in self.current_words:
            self.word_list.addItem(f"{word['text']} (x{word.get('weight', 1.0)})")

    def _on_add_group(self) -> None:
        from PySide6.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(self, "Add Group", "Group name:")
        if ok and name:
            self.hotwords_manager.add_group(name)
            self._load_groups()
            self._select_group(name)

    def _on_remove_group(self) -> None:
        if not self.current_group:
            return

        from PySide6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "Remove Group",
            f"Remove group '{self.current_group}'?",
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.hotwords_manager.remove_group(self.current_group)
            self._load_groups()

    def _on_add_word(self) -> None:
        if not self.current_group:
            return

        word = self.word_input.text().strip()
        if not word:
            return

        weight = self.weight_slider.value() / 10.0
        self.hotwords_manager.add_word(self.current_group, word, weight)
        self.word_input.clear()
        self._load_words()

    def _on_remove_word(self) -> None:
        if not self.current_group:
            return

        index = self.word_list.currentRow()
        if index >= 0 and index < len(self.current_words):
            word = self.current_words[index]["text"]
            self.hotwords_manager.remove_word(self.current_group, word)
            self._load_words()

    def _select_group(self, name: str) -> None:
        for i in range(self.group_list.count()):
            if self.group_list.item(i).text() == name:
                self.group_list.setCurrentRow(i)
                break
