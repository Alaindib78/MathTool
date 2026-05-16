from PySide6.QtCore import Signal

from PySide6.QtGui import QFont

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFontComboBox,
    QFormLayout,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


DEFAULT_PREFERENCES = {
    "theme": "Dark",
    "editor_font_family": "Consolas",
    "editor_font_size": 12,
    "output_font_size": 11,
    "tab_width": 4,
    "word_wrap": False,
    "auto_indent": True,
    "highlight_current_line": True,
    "show_line_numbers": True,
}


THEMES = {
    "Dark": {
        "window_background": "#1E1E1E",
        "panel_background": "#252526",
        "secondary_background": "#2E2E32",
        "hover_background": "#3E3E42",
        "pressed_background": "#005A9E",
        "accent": "#007ACC",
        "accent_hover": "#1084D7",
        "success": "#107C10",
        "text": "#D4D4D4",
        "muted_text": "#A0A0A0",
        "disabled_text": "#6A6A6A",
        "border": "#3E3E42",
        "editor_background": "#1E1E1E",
        "editor_foreground": "#D4D4D4",
        "editor_border": "#3E3E42",
        "gutter_background": "#252526",
        "line_number": "#858585",
        "current_line_number": "#CCCCCC",
        "current_line_background": "#2A2D2E",
        "debug_line_background": "#3A3320",
        "breakpoint": "#E51400",
        "breakpoint_border": "#F14C4C",
        "execution_arrow": "#DCDCAA",
        "table_alternate": "#252526",
        "input_background": "#1E1E1E",
    },
    "Light": {
        "window_background": "#F3F3F3",
        "panel_background": "#FFFFFF",
        "secondary_background": "#EDEDED",
        "hover_background": "#E5F1FB",
        "pressed_background": "#C7E0F4",
        "accent": "#0067C0",
        "accent_hover": "#0078D4",
        "success": "#0E7A0D",
        "text": "#1F1F1F",
        "muted_text": "#555555",
        "disabled_text": "#9A9A9A",
        "border": "#D0D0D0",
        "editor_background": "#FFFFFF",
        "editor_foreground": "#1E1E1E",
        "editor_border": "#D0D0D0",
        "gutter_background": "#F3F3F3",
        "line_number": "#6E7681",
        "current_line_number": "#24292F",
        "current_line_background": "#EAF3FF",
        "debug_line_background": "#FFF4CE",
        "breakpoint": "#D13438",
        "breakpoint_border": "#A4262C",
        "execution_arrow": "#B8860B",
        "table_alternate": "#F7F7F7",
        "input_background": "#FFFFFF",
    },
    "High Contrast": {
        "window_background": "#000000",
        "panel_background": "#111111",
        "secondary_background": "#1F1F1F",
        "hover_background": "#333333",
        "pressed_background": "#005A9E",
        "accent": "#00A2FF",
        "accent_hover": "#33B5FF",
        "success": "#00B050",
        "text": "#FFFFFF",
        "muted_text": "#D0D0D0",
        "disabled_text": "#777777",
        "border": "#FFFFFF",
        "editor_background": "#000000",
        "editor_foreground": "#FFFFFF",
        "editor_border": "#FFFFFF",
        "gutter_background": "#111111",
        "line_number": "#C0C0C0",
        "current_line_number": "#FFFFFF",
        "current_line_background": "#1F1F1F",
        "debug_line_background": "#403A00",
        "breakpoint": "#FF3B30",
        "breakpoint_border": "#FFFFFF",
        "execution_arrow": "#FFFF00",
        "table_alternate": "#111111",
        "input_background": "#000000",
    },
}


def load_preferences(settings):
    preferences = {}

    for key, default in DEFAULT_PREFERENCES.items():
        value = settings.value(key, default)

        if isinstance(default, bool):
            value = str(value).lower() in (
                "1",
                "true",
                "yes",
            )

        elif isinstance(default, int):
            value = int(value)

        preferences[key] = value

    if preferences["theme"] not in THEMES:
        preferences["theme"] = DEFAULT_PREFERENCES["theme"]

    return preferences


def save_preference(settings, key, value):
    settings.setValue(key, value)

    settings.sync()


def theme_for_preferences(preferences):
    return THEMES.get(
        preferences.get("theme"),
        THEMES[DEFAULT_PREFERENCES["theme"]],
    )


def build_stylesheet(preferences):
    colors = theme_for_preferences(preferences)

    return f"""
    QMainWindow {{
        background-color: {colors["window_background"]};
        color: {colors["text"]};
    }}

    QMenuBar {{
        background-color: {colors["panel_background"]};
        color: {colors["text"]};
        border-bottom: 1px solid {colors["border"]};
        padding: 2px;
        spacing: 0px;
    }}

    QMenuBar::item {{
        background: transparent;
        padding: 6px 12px;
        margin: 0px;
        min-height: 18px;
    }}

    QMenuBar::item:selected {{
        background-color: {colors["hover_background"]};
    }}

    QMenuBar::item:pressed {{
        background-color: {colors["accent"]};
    }}

    QMenu {{
        background-color: {colors["panel_background"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
        padding: 4px 0px;
    }}

    QMenu::item {{
        padding: 6px 40px 6px 28px;
        min-width: 180px;
        min-height: 20px;
    }}

    QMenu::item:selected {{
        background-color: {colors["accent"]};
        color: #FFFFFF;
    }}

    QMenu::item:pressed {{
        background-color: {colors["pressed_background"]};
    }}

    QMenu::separator {{
        background-color: {colors["border"]};
        height: 1px;
        margin: 5px 8px;
    }}

    QToolBar {{
        background-color: {colors["panel_background"]};
        border-bottom: 1px solid {colors["border"]};
        spacing: 3px;
        padding: 5px;
    }}

    QToolBar::separator {{
        background-color: {colors["border"]};
        width: 1px;
        margin: 0px 3px;
    }}

    QPushButton {{
        background-color: {colors["accent"]};
        color: #FFFFFF;
        border: none;
        border-radius: 4px;
        padding: 6px 16px;
        font-weight: bold;
        font-size: 11px;
    }}

    QPushButton:hover {{
        background-color: {colors["accent_hover"]};
    }}

    QPushButton:pressed {{
        background-color: {colors["pressed_background"]};
    }}

    QPushButton:disabled {{
        background-color: {colors["hover_background"]};
        color: {colors["disabled_text"]};
    }}

    QPushButton#secondaryButton {{
        background-color: {colors["secondary_background"]};
        color: {colors["text"]};
    }}

    QPushButton#secondaryButton:hover {{
        background-color: {colors["hover_background"]};
    }}

    QPushButton#secondaryButton:pressed {{
        background-color: {colors["pressed_background"]};
    }}

    QPlainTextEdit {{
        background-color: {colors["editor_background"]};
        color: {colors["editor_foreground"]};
        border: 1px solid {colors["editor_border"]};
        border-radius: 3px;
        font-family: '{preferences["editor_font_family"]}', 'Courier New', monospace;
        font-size: {preferences["editor_font_size"]}pt;
    }}

    QTableWidget {{
        background-color: {colors["input_background"]};
        alternate-background-color: {colors["table_alternate"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
        gridline-color: {colors["border"]};
    }}

    QTableWidget::item {{
        padding: 4px;
        border-bottom: 1px solid {colors["border"]};
    }}

    QTableWidget::item:selected {{
        background-color: {colors["accent"]};
        color: #FFFFFF;
    }}

    QHeaderView::section {{
        background-color: {colors["panel_background"]};
        color: {colors["text"]};
        padding: 4px;
        border: none;
        border-right: 1px solid {colors["border"]};
        border-bottom: 1px solid {colors["border"]};
        font-weight: bold;
    }}

    QDockWidget {{
        background-color: {colors["window_background"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
    }}

    QDockWidget::title {{
        background-color: {colors["panel_background"]};
        padding: 6px;
        border-bottom: 1px solid {colors["border"]};
    }}

    QTabWidget::pane {{
        border: 1px solid {colors["border"]};
    }}

    QTabBar::tab {{
        background-color: {colors["secondary_background"]};
        color: {colors["muted_text"]};
        padding: 8px 16px;
        border-right: 1px solid {colors["border"]};
        margin-right: 2px;
    }}

    QTabBar::tab:selected {{
        background-color: {colors["window_background"]};
        color: {colors["text"]};
        border-bottom: 2px solid {colors["accent"]};
    }}

    QTabBar::tab:hover {{
        background-color: {colors["hover_background"]};
    }}

    QStatusBar {{
        background-color: {colors["panel_background"]};
        color: {colors["text"]};
        border-top: 1px solid {colors["border"]};
    }}

    QDialog {{
        background-color: {colors["window_background"]};
        color: {colors["text"]};
    }}

    QLabel {{
        color: {colors["text"]};
    }}

    QComboBox,
    QFontComboBox,
    QSpinBox,
    QLineEdit {{
        background-color: {colors["input_background"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
        border-radius: 3px;
        padding: 4px 6px;
        min-height: 22px;
    }}

    QComboBox QAbstractItemView,
    QFontComboBox QAbstractItemView {{
        background-color: {colors["panel_background"]};
        color: {colors["text"]};
        selection-background-color: {colors["accent"]};
    }}

    QCheckBox {{
        color: {colors["text"]};
        spacing: 8px;
    }}
    """


class OptionsDialog(QDialog):
    preference_changed = Signal(str, object)

    def __init__(self, preferences, parent=None):
        super().__init__(parent)

        self.preferences = preferences.copy()

        self.setWindowTitle("Options")

        self.resize(440, 320)

        layout = QVBoxLayout()

        self.setLayout(layout)

        tabs = QTabWidget()

        layout.addWidget(tabs)

        tabs.addTab(
            self._build_appearance_tab(),
            "Appearance",
        )

        tabs.addTab(
            self._build_editor_tab(),
            "Editor",
        )

        close_button = QPushButton("Close")

        close_button.clicked.connect(self.close)

        layout.addWidget(close_button)

    def _build_appearance_tab(self):
        widget = QWidget()

        form = QFormLayout()

        widget.setLayout(form)

        theme_combo = QComboBox()

        theme_combo.addItems(list(THEMES.keys()))

        theme_combo.setCurrentText(
            self.preferences["theme"]
        )

        theme_combo.currentTextChanged.connect(
            lambda value: self._set_preference(
                "theme",
                value,
            )
        )

        form.addRow("Theme", theme_combo)

        font_combo = QFontComboBox()

        font_combo.setCurrentFont(
            QFont(
                self.preferences[
                    "editor_font_family"
                ]
            )
        )

        font_combo.currentFontChanged.connect(
            lambda font: self._set_preference(
                "editor_font_family",
                font.family(),
            )
        )

        form.addRow("Editor font", font_combo)

        editor_size = self._spin_box(
            "editor_font_size",
            8,
            32,
        )

        form.addRow("Editor font size", editor_size)

        output_size = self._spin_box(
            "output_font_size",
            8,
            32,
        )

        form.addRow("Console font size", output_size)

        return widget

    def _build_editor_tab(self):
        widget = QWidget()

        form = QFormLayout()

        widget.setLayout(form)

        tab_width = self._spin_box(
            "tab_width",
            2,
            12,
        )

        form.addRow("Tab width", tab_width)

        form.addRow(
            "Word wrap",
            self._check_box("word_wrap"),
        )

        form.addRow(
            "Auto indent",
            self._check_box("auto_indent"),
        )

        form.addRow(
            "Highlight current line",
            self._check_box(
                "highlight_current_line"
            ),
        )

        form.addRow(
            "Line numbers",
            self._check_box("show_line_numbers"),
        )

        return widget

    def _spin_box(self, key, minimum, maximum):
        spin_box = QSpinBox()

        spin_box.setRange(minimum, maximum)

        spin_box.setValue(
            int(self.preferences[key])
        )

        spin_box.valueChanged.connect(
            lambda value: self._set_preference(
                key,
                value,
            )
        )

        return spin_box

    def _check_box(self, key):
        check_box = QCheckBox()

        check_box.setChecked(
            bool(self.preferences[key])
        )

        check_box.toggled.connect(
            lambda value: self._set_preference(
                key,
                value,
            )
        )

        return check_box

    def _set_preference(self, key, value):
        self.preferences[key] = value

        self.preference_changed.emit(
            key,
            value,
        )
