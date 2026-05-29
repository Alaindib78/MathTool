import ast
import os
from datetime import datetime
from tkinter import font
from unittest import result

from PySide6.QtWidgets import (
    QAbstractItemView,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QToolBar,
    QTableWidget,
    QTableWidgetItem,
    QDockWidget,
    QHeaderView,
    QTabWidget,
    QFileDialog,
    QMessageBox,
    QInputDialog,
    QCheckBox,
    QLabel,
    QStatusBar,
    QLineEdit,
    QMenu,
)

from PySide6.QtGui import (
    QAction,
    QKeySequence,
    QIcon,
    QFont,
    QColor,
    QTextCursor,
    QTextCharFormat,
)

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QSizePolicy
from matplotlib import text

from PySide6.QtCore import (
    Qt,
    QThread,
    QSettings,
    Signal,
)

from core.engine import MathToolSession
from core.calculus import FunctionHandle
from core.control import is_lti_model
from core.runtime.context import RESERVED_CONSTANTS
from core.runtime.formatting import format_value, output_suffix
from core.runtime.function_resolver import (
    top_level_function_declarations,
)
from core.runtime.symbolic import SymbolicValue
from gui.code_editor import (
    CodeEditor
)

from gui.syntax_highlighter import (
    MathToolSyntaxHighlighter
)

from gui.command_window import (
    CommandWindow
)

from gui.variable_editor import (
    VariableEditor
)

from core.debugger.debugger import (
    Debugger
)

from gui.execution_worker import (
    ExecutionWorker
)

from gui.documentation_panel import (
    DocumentationPanel
)

from gui.plot_engine import (
    GuiPlotEngine
)

from gui.preferences import (
    OptionsDialog,
    build_stylesheet,
    load_preferences,
    save_preference,
    theme_for_preferences,
)


class MainWindow(QMainWindow):
    debug_pause_requested = Signal(int)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("MathTool")

        self.resize(1400, 900)

        self.plot_engine = GuiPlotEngine()

        self.debugger = Debugger()

        self.debug_pause_requested.connect(
            self.handle_debug_pause
        )

        self.debugger.pause_callback = (
            self.on_debug_pause
        )

        self.session = MathToolSession(
            output_callback=self.route_output,
            plot_engine=self.plot_engine,
            debugger=self.debugger,
        )

        self.context = self.session.context

        self.interpreter = self.session.interpreter

        self.semantic = self.session.semantic

        self.default_working_directory = (
            self.context.current_working_directory
        )

        self.settings = QSettings(
            "MathTool",
            "MathTool",
        )

        self.preferences = load_preferences(
            self.settings
        )

        self.load_runtime_settings()

        self.options_dialog = None

        # Apply modern styling
        self.apply_stylesheet()

        self.setup_ui()

        self.setup_current_directory_panel()

        self.setup_workspace_panel()

        self.setup_path_manager_panel()

        self.setup_documentation_panel()

        self.setup_command_window()

        self.setup_toolbar()

        self.setup_menu()

        self.setup_status_bar()

        self.execution_thread = None

        self.execution_worker = None

        self.execution_editor = None

        self.context.path_changed_callback = (
            self.update_runtime_path_ui
        )

        self.update_runtime_path_ui()

        self.apply_preferences()

    def apply_stylesheet(self):
        """Apply a modern dark theme stylesheet"""
        if hasattr(self, "preferences"):
            self.setStyleSheet(
                build_stylesheet(
                    self.preferences
                )
            )

            return

        stylesheet = """
        QMainWindow {
            background-color: #1E1E1E;
            color: #D4D4D4;
        }
        
        QMenuBar {
            background-color: #252526;
            color: #D4D4D4;
            border-bottom: 1px solid #3E3E42;
            padding: 2px;
            spacing: 0px;
        }

        QMenuBar::item {
            background: transparent;
            padding: 6px 12px;
            margin: 0px;
            min-height: 18px;
        }
        
        QMenuBar::item:selected {
            background-color: #3E3E42;
        }
        
        QMenuBar::item:pressed {
            background-color: #007ACC;
        }
        
        QMenu {
            background-color: #252526;
            color: #D4D4D4;
            border: 1px solid #3E3E42;
            padding: 4px 0px;
        }

        QMenu::item {
            padding: 6px 40px 6px 28px;
            min-width: 180px;
            min-height: 20px;
        }
        
        QMenu::item:selected {
            background-color: #007ACC;
        }
        
        QMenu::item:pressed {
            background-color: #005A9E;
        }
        
        QMenu::separator {
            background-color: #3E3E42;
            height: 1px;
            margin: 5px 8px;
        }
        
        QToolBar {
            background-color: #252526;
            border-bottom: 1px solid #3E3E42;
            spacing: 3px;
            padding: 5px;
        }
        
        QToolBar::separator {
            background-color: #3E3E42;
            width: 1px;
            margin: 0px 3px;
        }
        
        QPushButton {
            background-color: #007ACC;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 16px;
            font-weight: bold;
            font-size: 11px;
        }
        
        QPushButton:hover {
            background-color: #1084D7;
        }
        
        QPushButton:pressed {
            background-color: #005A9E;
        }
        
        QPushButton:disabled {
            background-color: #3E3E42;
            color: #6A6A6A;
        }
        
        QPushButton#secondaryButton {
            background-color: #3E3E42;
            color: #D4D4D4;
        }
        
        QPushButton#secondaryButton:hover {
            background-color: #4E4E54;
        }
        
        QPushButton#secondaryButton:pressed {
            background-color: #2E2E32;
        }
        
        QPlainTextEdit {
            background-color: #1E1E1E;
            color: #D4D4D4;
            border: 1px solid #3E3E42;
            border-radius: 3px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 11px;
        }
        
        QTableWidget {
            background-color: #1E1E1E;
            alternate-background-color: #252526;
            color: #D4D4D4;
            border: 1px solid #3E3E42;
            gridline-color: #3E3E42;
        }
        
        QTableWidget::item {
            padding: 4px;
            border-bottom: 1px solid #3E3E42;
        }
        
        QTableWidget::item:selected {
            background-color: #007ACC;
        }
        
        QHeaderView::section {
            background-color: #252526;
            color: #D4D4D4;
            padding: 4px;
            border: none;
            border-right: 1px solid #3E3E42;
            border-bottom: 1px solid #3E3E42;
            font-weight: bold;
        }
        
        QDockWidget {
            background-color: #1E1E1E;
            color: #D4D4D4;
            border: 1px solid #3E3E42;
            titlebar-close-icon: url(close.png);
        }
        
        QDockWidget::title {
            background-color: #252526;
            padding: 6px;
            border-bottom: 1px solid #3E3E42;
        }
        
        QTabWidget::pane {
            border: 1px solid #3E3E42;
        }
        
        QTabBar::tab {
            background-color: #2E2E32;
            color: #A0A0A0;
            padding: 8px 16px;
            border-right: 1px solid #3E3E42;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #1E1E1E;
            color: #D4D4D4;
            border-bottom: 2px solid #007ACC;
        }
        
        QTabBar::tab:hover {
            background-color: #3E3E42;
        }
        
        QTabBar::close-button {
            margin-left: 8px;
        }
        
        QStatusBar {
            background-color: #252526;
            color: #D4D4D4;
            border-top: 1px solid #3E3E42;
        }
        
        QInputDialog {
            background-color: #1E1E1E;
            color: #D4D4D4;
        }
        
        QMessageBox {
            background-color: #1E1E1E;
        }
        
        QMessageBox QLabel {
            color: #D4D4D4;
        }
        
        QMessageBox QPushButton {
            min-width: 60px;
        }
        """
        self.setStyleSheet(stylesheet)

    def apply_preferences(self):
        self.apply_stylesheet()

        colors = theme_for_preferences(
            self.preferences
        )

        if hasattr(self, "main_splitter"):
            self.main_splitter.setStyleSheet(
                f"""
                QSplitter::handle {{
                    background-color: {colors["border"]};
                }}
                QSplitter::handle:hover {{
                    background-color: {colors["accent"]};
                }}
                """
            )

        if hasattr(self, "console_label"):
            self.console_label.setStyleSheet(
                f"""
                color: {colors["text"]};
                font-weight: bold;
                font-size: 11px;
                padding: 6px 8px;
                background-color: {colors["panel_background"]};
                border-bottom: 1px solid {colors["border"]};
                """
            )

        if hasattr(self, "run_button"):
            self.run_button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {colors["success"]};
                    color: #FFFFFF;
                    padding: 6px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {colors["success"]};
                }}
                QPushButton:disabled {{
                    background-color: {colors["hover_background"]};
                    color: {colors["disabled_text"]};
                }}
                """
            )

        if hasattr(self, "workspace_dock"):
            self.workspace_dock.setStyleSheet("")

        if hasattr(self, "command_dock"):
            self.command_dock.setStyleSheet("")

        if hasattr(self, "status_label"):
            self.statusBar().setStyleSheet(
                f"""
                QStatusBar {{
                    background-color: {colors["panel_background"]};
                    color: {colors["text"]};
                    border-top: 1px solid {colors["border"]};
                }}
                """
            )

        for editor in self.all_code_editors():
            self.apply_editor_preferences(editor)

        if hasattr(self, "console"):
            self.apply_plain_text_preferences(
                self.console,
                self.preferences["output_font_size"],
            )

        if hasattr(self, "command_window"):
            self.apply_plain_text_preferences(
                self.command_window,
                self.preferences["output_font_size"],
                border="none",
            )

    def all_code_editors(self):
        if not hasattr(self, "tabs"):
            return []

        return [
            self.tabs.widget(index)
            for index in range(self.tabs.count())
            if isinstance(
                self.tabs.widget(index),
                CodeEditor,
            )
        ]

    def apply_editor_preferences(self, editor):
        colors = theme_for_preferences(
            self.preferences
        )

        editor.apply_editor_preferences(
            self.preferences,
            colors,
        )

        if hasattr(editor, "highlighter"):
            editor.highlighter.set_theme(
                self.preferences["theme"]
            )

    def apply_plain_text_preferences(
        self,
        widget,
        font_size,
        border=None,
    ):
        colors = theme_for_preferences(
            self.preferences
        )

        font = QFont(
            self.preferences["editor_font_family"],
            int(font_size),
        )

        widget.setFont(font)

        border_style = (
            border
            if border is not None
            else f"1px solid {colors['editor_border']}"
        )

        widget.setStyleSheet(
            f"""
            QPlainTextEdit {{
                background-color: {colors["editor_background"]};
                color: {colors["editor_foreground"]};
                border: {border_style};
                border-radius: 3px;
                font-family: '{font.family()}';
                font-size: {font.pointSize()}pt;
            }}
            """
        )

        if hasattr(widget, "set_normal_text_color"):
            widget.set_normal_text_color(
                colors["editor_foreground"]
            )

    def set_preference(self, key, value):
        self.preferences[key] = value

        save_preference(
            self.settings,
            key,
            value,
        )

        self.apply_preferences()

    def load_runtime_settings(self):
        directory = self.settings.value(
            "runtime/current_working_directory",
            self.context.current_working_directory,
        )

        try:
            self.context.set_current_working_directory(
                directory
            )
        except Exception:
            pass

        paths = self.settings.value(
            "runtime/search_paths",
            [],
        )

        if isinstance(paths, str):
            paths = [paths] if paths else []

        if paths is None:
            paths = []

        self.context.search_paths = []

        for path in paths:
            try:
                self.context.add_search_path(path)
            except Exception:
                continue

        self.include_subdirectories_on_add = (
            self.setting_to_bool(
                self.settings.value(
                    "runtime/include_subdirectories_on_add",
                    True,
                ),
                True,
            )
        )

    def save_runtime_settings(self):
        self.settings.setValue(
            "runtime/current_working_directory",
            self.context.current_working_directory,
        )

        self.settings.setValue(
            "runtime/search_paths",
            self.context.search_paths,
        )

        self.settings.setValue(
            "runtime/include_subdirectories_on_add",
            self.include_subdirectories_on_add,
        )

        self.settings.sync()

    def setting_to_bool(self, value, default=False):
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            return value.strip().lower() in (
                "1",
                "true",
                "yes",
                "on",
            )

        if value is None:
            return default

        return bool(value)

    def update_runtime_path_ui(self):
        self.update_working_directory_status()
        self.refresh_directory_browser()
        self.refresh_path_table()
        self.update_function_diagnostics()

        if hasattr(self, "documentation_panel"):
            self.documentation_panel.refresh()

    def choose_current_working_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Set Current Working Directory",
            self.context.current_working_directory,
        )

        if not directory:
            return

        self.apply_current_working_directory(
            directory
        )

    def apply_current_working_directory(
        self,
        directory,
    ):
        previous_directory = (
            self.context.current_working_directory
        )

        try:
            self.context.set_current_working_directory(
                directory
            )

            self.context.validate_function_paths()
        except Exception as error:
            self.context.set_current_working_directory(
                previous_directory
            )

            QMessageBox.critical(
                self,
                "Working Directory Error",
                str(error),
            )

            return

        self.save_runtime_settings()

        self.update_runtime_path_ui()

        self.console.appendPlainText(
            f"Current directory: "
            f"{self.context.current_working_directory}"
        )

    def reset_current_working_directory(self):
        self.apply_current_working_directory(
            self.default_working_directory
        )

    def go_to_parent_directory(self):
        parent = os.path.dirname(
            self.context.current_working_directory
        )

        if (
            parent
            and parent != self.context.current_working_directory
        ):
            self.apply_current_working_directory(
                parent
            )

    def add_search_path(
        self,
        directory=None,
        include_subdirectories=None,
    ):
        if isinstance(directory, bool):
            directory = None

        if directory is None:
            directory = QFileDialog.getExistingDirectory(
                self,
                "Add Directory to Search Path",
                self.context.current_working_directory,
            )

        if not directory:
            return

        if include_subdirectories is None:
            include_subdirectories = (
                self.include_subdirectories_for_path_add()
            )

        previous_paths = list(self.context.search_paths)

        try:
            directories = self.search_path_directories(
                directory,
                include_subdirectories,
            )

            for path in directories:
                self.context.add_search_path(path)

            self.context.validate_function_paths()
        except Exception as error:
            self.context.set_search_paths(
                previous_paths
            )

            QMessageBox.critical(
                self,
                "Search Path Error",
                str(error),
            )

            return

        self.save_runtime_settings()

        self.update_runtime_path_ui()

        if len(directories) == 1:
            message = f"Added to path: {directories[0]}"
        else:
            message = (
                f"Added {len(directories)} directories "
                f"to path: {directories[0]}"
            )

        self.console.appendPlainText(
            message
        )

    def include_subdirectories_for_path_add(self):
        if hasattr(self, "include_subdirectories_checkbox"):
            return (
                self
                .include_subdirectories_checkbox
                .isChecked()
            )

        return getattr(
            self,
            "include_subdirectories_on_add",
            True,
        )

    def set_include_subdirectories_on_add(self, checked):
        self.include_subdirectories_on_add = bool(checked)

        self.save_runtime_settings()

    def search_path_directories(
        self,
        directory,
        include_subdirectories=False,
    ):
        root = self.context.normalize_directory(directory)

        directories = [root]

        if include_subdirectories:
            for current, child_names, _ in os.walk(root):
                child_names.sort(key=str.lower)

                if current == root:
                    continue

                try:
                    normalized_current = (
                        self
                        .context
                        .normalize_directory(current)
                    )
                except ValueError:
                    child_names.clear()
                    continue

                directories.append(normalized_current)

        unique_directories = []
        seen = set()

        for path in directories:
            if path in seen:
                continue

            seen.add(path)
            unique_directories.append(path)

        return unique_directories

    def remove_search_path(self):
        if not self.context.search_paths:
            QMessageBox.information(
                self,
                "Search Path",
                "The search path is empty.",
            )

            return

        row = self.selected_path_row()

        if row is not None:
            directory = self.context.search_paths[row]

            self.remove_search_path_at(row)

            self.console.appendPlainText(
                f"Removed from path: {directory}"
            )

            return

        directory, ok = QInputDialog.getItem(
            self,
            "Remove Search Path",
            "Directory:",
            self.context.search_paths,
            0,
            False,
        )

        if not ok or not directory:
            return

        if directory in self.context.search_paths:
            self.remove_search_path_at(
                self.context.search_paths.index(
                    directory
                )
            )

            self.console.appendPlainText(
                f"Removed from path: {directory}"
            )

    def remove_search_path_at(self, row):
        if row < 0 or row >= len(
            self.context.search_paths
        ):
            return

        del self.context.search_paths[row]

        self.context.function_resolver.invalidate()

        self.context.notify_path_changed()

        self.save_runtime_settings()

        self.update_runtime_path_ui()

    def move_selected_search_path_up(self):
        self.move_selected_search_path(-1)

    def move_selected_search_path_down(self):
        self.move_selected_search_path(1)

    def move_selected_search_path(self, direction):
        row = self.selected_path_row()

        if row is None:
            return

        target = row + direction

        if (
            target < 0
            or target >= len(self.context.search_paths)
        ):
            return

        paths = self.context.search_paths

        paths[row], paths[target] = (
            paths[target],
            paths[row],
        )

        self.context.function_resolver.invalidate()

        self.context.notify_path_changed()

        self.save_runtime_settings()

        self.refresh_path_table()

        self.select_path_row(target)

        self.update_function_diagnostics()

    def show_search_path(self):
        path_lines = [
            "Core library:",
            *(
                self.context.library_paths
                or ["(not available)"]
            ),
            "",
            "Current directory:",
            self.context.current_working_directory,
            "",
            "Search path:",
        ]

        if self.context.search_paths:
            path_lines.extend(
                self.context.search_paths
            )
        else:
            path_lines.append("(empty)")

        QMessageBox.information(
            self,
            "Function Search Path",
            "\n".join(path_lines),
        )

    def show_path_manager(self):
        if hasattr(self, "path_manager_dock"):
            self.path_manager_dock.show()
            self.path_manager_dock.raise_()

    def update_working_directory_status(self):
        directory = self.context.current_working_directory

        if hasattr(self, "cwd_label"):
            self.cwd_label.setText(
                f"Current directory: {directory}"
            )

        if hasattr(self, "cwd_path_edit"):
            self.cwd_path_edit.setText(directory)

        if hasattr(self, "cwd_browser_label"):
            self.cwd_browser_label.setText(
                "Current working directory"
            )

    def show_options_dialog(self):
        if (
            self.options_dialog is not None
            and self.options_dialog.isVisible()
        ):
            self.options_dialog.raise_()

            self.options_dialog.activateWindow()

            return

        self.options_dialog = OptionsDialog(
            self.preferences,
            self,
        )

        self.options_dialog.preference_changed.connect(
            self.set_preference
        )

        self.options_dialog.finished.connect(
            lambda _: setattr(
                self,
                "options_dialog",
                None,
            )
        )

        self.options_dialog.show()

    def setup_ui(self):
        central_widget = QWidget()

        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        central_widget.setLayout(layout)

        # ---------------------------------
        # Splitter
        # ---------------------------------

        splitter = QSplitter(Qt.Vertical)

        self.main_splitter = splitter

        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #3E3E42;
            }
            QSplitter::handle:hover {
                background-color: #007ACC;
            }
        """)

        layout.addWidget(splitter)

        # ---------------------------------
        # Tabbed Editor
        # ---------------------------------

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(
            self.close_tab
        )
        self.tabs.currentChanged.connect(
            self.sync_breakpoints
        )

        splitter.addWidget(self.tabs)

        self.create_new_tab()

        # ---------------------------------
        # Output Console
        # ---------------------------------

        console_container = QWidget()
        console_layout = QVBoxLayout()
        console_layout.setContentsMargins(0, 0, 0, 0)
        console_layout.setSpacing(0)

        console_label = QLabel("Output")

        self.console_label = console_label

        console_label.setStyleSheet("""
            color: #D4D4D4;
            font-weight: bold;
            font-size: 11px;
            padding: 6px 8px;
            background-color: #252526;
            border-bottom: 1px solid #3E3E42;
        """)
        console_layout.addWidget(console_label)

        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setContextMenuPolicy(
            Qt.CustomContextMenu
        )
        self.console.customContextMenuRequested.connect(
            self.show_output_context_menu
        )

        font = QFont("Consolas", 11)
        self.console.setFont(font)

        console_layout.addWidget(self.console)
        console_container.setLayout(console_layout)

        splitter.addWidget(console_container)

        splitter.setSizes([650, 250])

    def setup_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))

        self.addToolBar(toolbar)

        # Run section
        self.run_button = QPushButton("▶ Run")
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #107C10;
                padding: 6px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #107C10;
                opacity: 0.8;
            }
        """)
        self.run_button.clicked.connect(self.run_code)
        toolbar.addWidget(self.run_button)

        self.debug_button = QPushButton("Debug")
        self.debug_button.setObjectName("secondaryButton")
        self.debug_button.clicked.connect(
            self.start_debugging
        )
        toolbar.addWidget(self.debug_button)

        toolbar.addSeparator()

        # File operations
        self.new_button = QPushButton("+ New")
        self.new_button.setObjectName("secondaryButton")
        self.new_button.clicked.connect(self.new_file)
        toolbar.addWidget(self.new_button)

        open_button = QPushButton("📂 Open")
        open_button.setObjectName("secondaryButton")
        open_button.clicked.connect(self.open_file)
        toolbar.addWidget(open_button)

        save_button = QPushButton("💾 Save")
        save_button.setObjectName("secondaryButton")
        save_button.clicked.connect(self.save_file)
        toolbar.addWidget(save_button)

        toolbar.addSeparator()

        # Workspace operations
        refresh_workspace_button = QPushButton("🔄 Workspace")
        refresh_workspace_button.setObjectName("secondaryButton")
        refresh_workspace_button.clicked.connect(
            self.refresh_workspace
        )
        toolbar.addWidget(refresh_workspace_button)

        clear_workspace_button = QPushButton("🗑️ Clear")
        clear_workspace_button.setObjectName("secondaryButton")
        clear_workspace_button.clicked.connect(
            self.clear_workspace
        )
        toolbar.addWidget(clear_workspace_button)

        toolbar.addSeparator()

        # Debug operations
        continue_button = QPushButton("▶ Continue")
        continue_button.setObjectName("secondaryButton")
        continue_button.clicked.connect(
            self.debug_continue
        )
        toolbar.addWidget(continue_button)

        step_button = QPushButton("↓ Step")
        step_button.setObjectName("secondaryButton")
        step_button.clicked.connect(self.debug_step)
        toolbar.addWidget(step_button)

        breakpoint_button = QPushButton("🔴 Breakpoint")
        breakpoint_button.setObjectName("secondaryButton")
        breakpoint_button.clicked.connect(
            self.add_breakpoint_dialog
        )
        toolbar.addWidget(breakpoint_button)

        # Spacer
 #       spacer = QWidget()
 #       spacer.setSizePolicy(
 #           spacer.sizePolicy().Expanding,
 #           spacer.sizePolicy().Expanding,
 #       )
 #       toolbar.addWidget(spacer)

        # Spacer
        spacer = QWidget()
 #       from PySide6.QtWidgets import QSizePolicy
        spacer.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )
        toolbar.addWidget(spacer)

        stop_button = QPushButton(
            "Stop"
        )

        stop_button.clicked.connect(
            self.stop_execution
        )

        toolbar.addWidget(stop_button)

    def run_code(self):
        self.start_execution(debug=False)

    def start_debugging(self):
        self.start_execution(debug=True)

    def start_execution(self, debug=False):
        editor = self.current_editor()

        if editor is None:
            return

        source = editor.toPlainText()

        # Prevent multiple executions
        if (
            self.execution_thread
            and self.execution_thread.isRunning()
        ):
            self.console.appendPlainText(
                "Execution already running"
            )

            return

        self.clear_debug_highlights()

        if debug:
            self.sync_breakpoints()

            self.debugger.start_session()

            self.execution_editor = editor

        else:
            self.debugger.stop_session()

            self.execution_editor = None
        
        self.console.appendPlainText(
            "Debugging...\n"
            if debug
            else "Running...\n"
        )

        self.run_button.setEnabled(False)

        if hasattr(self, "debug_button"):
            self.debug_button.setEnabled(False)

        # ---------------------------------
        # Create thread
        # ---------------------------------

        self.execution_thread = QThread()

        self.execution_worker = (
            ExecutionWorker(
                source,
                self.session,
                source_path=editor.file_path,
            )
        )

        self.execution_worker.moveToThread(
            self.execution_thread
        )

        # ---------------------------------
        # Signals
        # ---------------------------------

        self.execution_thread.started.connect(
            self.execution_worker.run
        )

        self.execution_worker.finished.connect(
            self.on_execution_finished
        )

        self.execution_worker.error.connect(
            self.on_execution_error
        )

        self.execution_worker.output.connect(
            self.route_output
        )

        self.execution_worker.workspace_updated.connect(
            self.refresh_workspace
        )

        self.execution_worker.finished.connect(
            self.execution_thread.quit
        )

        self.execution_worker.error.connect(
            self.execution_thread.quit
        )

        self.execution_worker.finished.connect(
            self.execution_worker.deleteLater
        )

        self.execution_worker.error.connect(
            self.execution_worker.deleteLater
        )

        self.execution_thread.finished.connect(
            self.execution_thread.deleteLater
        )

        self.execution_thread.finished.connect(
            self.on_execution_thread_finished
        )

        # ---------------------------------
        # Start
        # ---------------------------------

        self.execution_thread.start()

    def on_execution_finished(self, result):
        self.clear_debug_highlights()

        self.debugger.stop_session()

        if result is not None:
            self.insert_output_text(
                self.console,
                format_value(
                    result,
                    self.context.display_format,
                )
                + output_suffix(
                    self.context.display_format
                ),
            )

        self.refresh_workspace()

        self.update_runtime_path_ui()

        if hasattr(self, "update_display_format_status"):
            self.update_display_format_status()

        self.console.appendPlainText(
            "Execution finished"
        )

        self.run_button.setEnabled(True)

        if hasattr(self, "debug_button"):
            self.debug_button.setEnabled(True)


    def on_execution_error(self, message):
        self.clear_debug_highlights()

        self.debugger.stop_session()

        if message:
            self.insert_output_text(
                self.console,
                message + "\n",
                "error",
            )

        self.refresh_workspace()

        self.update_runtime_path_ui()

        if hasattr(self, "update_display_format_status"):
            self.update_display_format_status()

        self.run_button.setEnabled(True)

        if hasattr(self, "debug_button"):
            self.debug_button.setEnabled(True)

    def on_execution_thread_finished(self):
        self.execution_thread = None
        self.execution_worker = None
        self.execution_editor = None

    def write_output(self, text):
        self.console.appendPlainText(
            format_value(
                text,
                self.context.display_format,
            )
        )

    def set_display_format(self, style):
        self.context.display_format.apply(style)
        self.update_display_format_status()

        if hasattr(self, "refresh_workspace"):
            self.refresh_workspace()

        self.refresh_variable_editors()

    def refresh_variable_editors(self):
        for editor in self.findChildren(VariableEditor):
            editor.refresh_display_format(
                self.context.display_format
            )

    def debug_continue(self):
        self.debugger.continue_execution()

        self.clear_debug_highlights()

    def debug_step(self):
        self.debugger.step()

    def on_debug_pause(self, node):
        line = getattr(node, "line", None)

        if line is None:
            return

        self.debug_pause_requested.emit(
            int(line)
        )

    def handle_debug_pause(self, line):
        editor = (
            self.execution_editor
            if self.execution_editor is not None
            else self.current_editor()
        )

        if editor is None:
            return

        index = self.tabs.indexOf(editor)

        if index != -1:
            self.tabs.setCurrentIndex(index)

        editor.highlight_debug_line(line)

        block = (
            editor.document()
            .findBlockByLineNumber(line - 1)
        )

        if not block.isValid():
            return

        cursor = editor.textCursor()

        cursor.setPosition(
            block.position()
        )

        editor.setTextCursor(cursor)

        editor.centerCursor()

        editor.setFocus()

        if hasattr(self, "status_label"):
            self.status_label.setText(
                f"Paused at line {line}"
            )

    def setup_menu(self):
        menu = self.menuBar()

        # File Menu
        self.file_menu = menu.addMenu("File")
        file_menu = self.file_menu

        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        close_tab_action = QAction("Close Tab", self)
        close_tab_action.setShortcut(QKeySequence.Close)
        close_tab_action.triggered.connect(
            self.close_current_tab
        )
        file_menu.addAction(close_tab_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        self.edit_menu = menu.addMenu("Edit")
        edit_menu = self.edit_menu

        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(
            lambda: self.invoke_editor_action("undo")
        )
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(
            lambda: self.invoke_editor_action("redo")
        )
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.triggered.connect(
            lambda: self.invoke_editor_action("selectAll")
        )
        edit_menu.addAction(select_all_action)

        # Run Menu
        self.run_menu = menu.addMenu("Run")
        run_menu = self.run_menu

        run_action = QAction("Run Code", self)
        run_action.setShortcut(QKeySequence("Ctrl+Return"))
        run_action.triggered.connect(self.run_code)
        run_menu.addAction(run_action)

        run_menu.addSeparator()

        clear_workspace_action = QAction(
            "Clear Workspace",
            self
        )
        clear_workspace_action.triggered.connect(
            self.clear_workspace
        )
        run_menu.addAction(clear_workspace_action)

        # Debug Menu
        self.debug_menu = menu.addMenu("Debug")
        debug_menu = self.debug_menu

        start_debug_action = QAction(
            "Start Debugging",
            self,
        )
        start_debug_action.triggered.connect(
            self.start_debugging
        )
        debug_menu.addAction(start_debug_action)

        debug_menu.addSeparator()

        continue_action = QAction("Continue", self)
        continue_action.setShortcut(
            QKeySequence("F5")
        )
        continue_action.triggered.connect(
            self.debug_continue
        )
        debug_menu.addAction(continue_action)

        step_action = QAction("Step", self)
        step_action.setShortcut(QKeySequence("F10"))
        step_action.triggered.connect(self.debug_step)
        debug_menu.addAction(step_action)

        debug_menu.addSeparator()

        breakpoint_action = QAction(
            "Add Breakpoint",
            self
        )
        breakpoint_action.setShortcut(
            QKeySequence("F9")
        )
        breakpoint_action.triggered.connect(
            self.add_breakpoint_dialog
        )
        debug_menu.addAction(breakpoint_action)

        # Format Menu
        self.format_menu = menu.addMenu("Format")
        format_menu = self.format_menu

        for label, style in (
            ("Short", "short"),
            ("Long", "long"),
            ("Short Scientific", "shortE"),
            ("Long Scientific", "longE"),
            ("Short General", "shortG"),
            ("Long General", "longG"),
            ("Short Engineering", "shortEng"),
            ("Long Engineering", "longEng"),
            ("Bank", "bank"),
            ("Rational", "rat"),
            ("Hex", "hex"),
            ("Signs", "+"),
        ):
            action = QAction(label, self)
            action.triggered.connect(
                lambda checked=False, s=style:
                self.set_display_format(s)
            )
            format_menu.addAction(action)

        format_menu.addSeparator()

        compact_action = QAction("Compact Spacing", self)
        compact_action.triggered.connect(
            lambda: self.set_display_format("compact")
        )
        format_menu.addAction(compact_action)

        loose_action = QAction("Loose Spacing", self)
        loose_action.triggered.connect(
            lambda: self.set_display_format("loose")
        )
        format_menu.addAction(loose_action)

        format_menu.addSeparator()

        default_format_action = QAction(
            "Reset to Default",
            self,
        )
        default_format_action.triggered.connect(
            lambda: self.set_display_format("default")
        )
        format_menu.addAction(default_format_action)

        # Tools Menu
        self.tools_menu = menu.addMenu("Tools")
        tools_menu = self.tools_menu

        set_directory_action = QAction(
            "Set Current Directory",
            self,
        )
        set_directory_action.triggered.connect(
            self.choose_current_working_directory
        )
        tools_menu.addAction(set_directory_action)

        add_path_action = QAction(
            "Add Directory to Path",
            self,
        )
        add_path_action.triggered.connect(
            self.add_search_path
        )
        tools_menu.addAction(add_path_action)

        remove_path_action = QAction(
            "Remove Directory from Path",
            self,
        )
        remove_path_action.triggered.connect(
            self.remove_search_path
        )
        tools_menu.addAction(remove_path_action)

        show_path_action = QAction(
            "Show Function Search Path",
            self,
        )
        show_path_action.triggered.connect(
            self.show_search_path
        )
        tools_menu.addAction(show_path_action)

        show_path_manager_action = QAction(
            "Show Function Path",
            self,
        )
        show_path_manager_action.triggered.connect(
            self.show_path_manager
        )
        tools_menu.addAction(show_path_manager_action)

        tools_menu.addSeparator()

        options_action = QAction("Options", self)
        options_action.triggered.connect(
            self.show_options_dialog
        )
        tools_menu.addAction(options_action)

        # Help Menu
        self.help_menu = menu.addMenu("Help")
        help_menu = self.help_menu

        about_action = QAction("About MathTool", self)
        help_menu.addAction(about_action)

        documentation_action = QAction(
            "Documentation",
            self
        )
        documentation_action.setShortcut(
            QKeySequence("F1")
        )
        documentation_action.triggered.connect(
            self.show_documentation_panel
        )
        help_menu.addAction(documentation_action)

        quick_help_action = QAction(
            "Quick Help Search",
            self,
        )
        quick_help_action.setShortcut(
            QKeySequence("Ctrl+K")
        )
        quick_help_action.triggered.connect(
            self.quick_help_search
        )
        help_menu.addAction(quick_help_action)

    def show_documentation_panel(self, topic=None):
        if isinstance(topic, bool):
            topic = None

        if not hasattr(self, "documentation_dock"):
            return

        self.documentation_dock.show()
        self.documentation_dock.raise_()

        if hasattr(self, "documentation_panel"):
            self.documentation_panel.refresh()

            if topic:
                self.documentation_panel.open_topic(topic)
            else:
                self.documentation_panel.focus_search()

    def quick_help_search(self):
        self.show_documentation_panel()

        if hasattr(self, "documentation_panel"):
            self.documentation_panel.focus_search()

    def setup_current_directory_panel(self):
        dock = QDockWidget("Current Folder", self)

        self.current_directory_dock = dock

        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        container.setLayout(layout)

        self.cwd_browser_label = QLabel(
            "Current working directory"
        )

        layout.addWidget(self.cwd_browser_label)

        self.cwd_path_edit = QLineEdit()
        self.cwd_path_edit.setReadOnly(True)

        layout.addWidget(self.cwd_path_edit)

        button_row = QHBoxLayout()

        change_button = QPushButton("Change")
        change_button.clicked.connect(
            self.choose_current_working_directory
        )
        button_row.addWidget(change_button)

        up_button = QPushButton("Up")
        up_button.clicked.connect(
            self.go_to_parent_directory
        )
        button_row.addWidget(up_button)

        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(
            self.reset_current_working_directory
        )
        button_row.addWidget(reset_button)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(
            self.refresh_directory_browser
        )
        button_row.addWidget(refresh_button)

        layout.addLayout(button_row)

        self.directory_filter_edit = QLineEdit()
        self.directory_filter_edit.setPlaceholderText(
            "Filter current folder"
        )
        self.directory_filter_edit.textChanged.connect(
            self.refresh_directory_browser
        )

        layout.addWidget(self.directory_filter_edit)

        self.directory_table = QTableWidget()
        self.directory_table.setColumnCount(3)
        self.directory_table.setHorizontalHeaderLabels(
            [
                "Name",
                "Type",
                "Function",
            ]
        )
        self.directory_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.directory_table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.directory_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )
        self.directory_table.setAlternatingRowColors(True)
        self.directory_table.cellDoubleClicked.connect(
            self.open_directory_entry
        )
        self.directory_table.setContextMenuPolicy(
            Qt.CustomContextMenu
        )
        self.directory_table.customContextMenuRequested.connect(
            self.show_directory_context_menu
        )

        header = self.directory_table.horizontalHeader()
        header.setSectionResizeMode(
            0,
            QHeaderView.Stretch,
        )
        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeToContents,
        )
        header.setSectionResizeMode(
            2,
            QHeaderView.Stretch,
        )

        layout.addWidget(self.directory_table)

        self.directory_feedback_label = QLabel()
        self.directory_feedback_label.setWordWrap(True)
        layout.addWidget(self.directory_feedback_label)

        dock.setWidget(container)

        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            dock,
        )

    def setup_path_manager_panel(self):
        dock = QDockWidget("Function Path", self)

        self.path_manager_dock = dock

        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        container.setLayout(layout)

        summary = QLabel(
            "External paths are searched after built-ins, "
            "same-file functions, the core library, and "
            "the current folder. "
            "Higher entries win when external paths contain "
            "the same function name."
        )
        summary.setWordWrap(True)

        self.path_summary_label = summary

        layout.addWidget(summary)

        self.path_table = QTableWidget()
        self.path_table.setColumnCount(3)
        self.path_table.setHorizontalHeaderLabels(
            [
                "Priority",
                "Directory",
                "Status",
            ]
        )
        self.path_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.path_table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.path_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )
        self.path_table.setAlternatingRowColors(True)

        path_header = self.path_table.horizontalHeader()
        path_header.setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents,
        )
        path_header.setSectionResizeMode(
            1,
            QHeaderView.Stretch,
        )
        path_header.setSectionResizeMode(
            2,
            QHeaderView.ResizeToContents,
        )

        layout.addWidget(self.path_table)

        include_subdirectories_checkbox = QCheckBox(
            "Include subdirectories when adding"
        )
        include_subdirectories_checkbox.setChecked(
            self.include_subdirectories_on_add
        )
        include_subdirectories_checkbox.toggled.connect(
            self.set_include_subdirectories_on_add
        )

        self.include_subdirectories_checkbox = (
            include_subdirectories_checkbox
        )

        layout.addWidget(include_subdirectories_checkbox)

        button_row = QHBoxLayout()

        add_button = QPushButton("Add")
        add_button.clicked.connect(
            self.add_search_path
        )
        button_row.addWidget(add_button)

        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(
            self.remove_search_path
        )
        button_row.addWidget(remove_button)

        up_button = QPushButton("Move Up")
        up_button.clicked.connect(
            self.move_selected_search_path_up
        )
        button_row.addWidget(up_button)

        down_button = QPushButton("Move Down")
        down_button.clicked.connect(
            self.move_selected_search_path_down
        )
        button_row.addWidget(down_button)

        layout.addLayout(button_row)

        self.path_feedback_label = QLabel()
        self.path_feedback_label.setWordWrap(True)
        layout.addWidget(self.path_feedback_label)

        dock.setWidget(container)

        self.addDockWidget(
            Qt.RightDockWidgetArea,
            dock,
        )

        dock.hide()

    def refresh_directory_browser(self):
        if not hasattr(self, "directory_table"):
            return

        directory = self.context.current_working_directory

        self.directory_table.setRowCount(0)

        try:
            entries = list(os.scandir(directory))
        except OSError as error:
            self.directory_feedback_label.setText(
                f"Unable to read current folder: {error}"
            )
            return

        filter_text = ""

        if hasattr(self, "directory_filter_edit"):
            filter_text = (
                self.directory_filter_edit
                .text()
                .strip()
                .lower()
            )

        entries = [
            entry
            for entry in entries
            if not filter_text
            or filter_text in entry.name.lower()
        ]

        entries.sort(
            key=lambda entry: (
                not entry.is_dir(),
                entry.name.lower(),
            )
        )

        self.directory_table.setRowCount(
            len(entries)
        )

        for row, entry in enumerate(entries):
            path = entry.path
            is_directory = entry.is_dir()
            extension = os.path.splitext(
                entry.name
            )[1].lower()

            if is_directory:
                type_text = "Folder"
                function_text = ""
            elif extension == ".m":
                type_text = "M-file"
                function_text = (
                    self.function_summary_for_file(path)
                )
            else:
                type_text = "File"
                function_text = ""

            name_item = QTableWidgetItem(entry.name)
            name_item.setData(Qt.UserRole, path)
            name_item.setData(
                Qt.UserRole + 1,
                is_directory,
            )

            if extension == ".m":
                name_item.setForeground(
                    QColor("#4FC3F7")
                )

            self.directory_table.setItem(
                row,
                0,
                name_item,
            )
            self.directory_table.setItem(
                row,
                1,
                QTableWidgetItem(type_text),
            )
            self.directory_table.setItem(
                row,
                2,
                QTableWidgetItem(function_text),
            )

        self.directory_table.resizeRowsToContents()

        self.directory_feedback_label.setText(
            f"{len(entries)} item(s). Double-click folders "
            f"to enter them or .m files to open them."
        )

    def function_summary_for_file(self, path):
        try:
            program = (
                self.context
                .function_resolver
                .parse_file(path)
            )
        except Exception:
            return "script or invalid function file"

        declarations = top_level_function_declarations(
            program
        )

        if not declarations:
            return "script"

        names = [
            declaration.name
            for declaration in declarations
        ]

        return ", ".join(names)

    def open_directory_entry(self, row, column):
        item = self.directory_table.item(row, 0)

        if item is None:
            return

        path = item.data(Qt.UserRole)
        is_directory = item.data(Qt.UserRole + 1)

        if is_directory:
            self.apply_current_working_directory(path)
            return

        self.open_file_path(path)

    def selected_directory_entry(self):
        if not hasattr(self, "directory_table"):
            return None, False

        selected = self.directory_table.selectedItems()

        if not selected:
            return None, False

        row = selected[0].row()
        item = self.directory_table.item(row, 0)

        if item is None:
            return None, False

        return (
            item.data(Qt.UserRole),
            bool(item.data(Qt.UserRole + 1)),
        )

    def open_selected_directory_entry(self):
        path, is_directory = (
            self.selected_directory_entry()
        )

        if not path:
            return

        if is_directory:
            self.apply_current_working_directory(path)
        else:
            self.open_file_path(path)

    def set_selected_directory_as_cwd(self):
        path, is_directory = (
            self.selected_directory_entry()
        )

        if path and is_directory:
            self.apply_current_working_directory(path)

    def add_selected_directory_to_path(self):
        path, is_directory = (
            self.selected_directory_entry()
        )

        if path and is_directory:
            self.add_search_path(path)

    def show_directory_context_menu(self, position):
        row = self.directory_table.rowAt(
            position.y()
        )

        if row < 0:
            return

        self.directory_table.selectRow(row)

        path, is_directory = (
            self.selected_directory_entry()
        )

        if not path:
            return

        menu = QMenu(self)

        if is_directory:
            open_action = menu.addAction(
                "Open Folder"
            )
            open_action.triggered.connect(
                self.open_selected_directory_entry
            )

            set_cwd_action = menu.addAction(
                "Set as Current Folder"
            )
            set_cwd_action.triggered.connect(
                self.set_selected_directory_as_cwd
            )

            add_path_action = menu.addAction(
                "Add to Function Path"
            )
            add_path_action.triggered.connect(
                self.add_selected_directory_to_path
            )
        else:
            open_action = menu.addAction("Open File")
            open_action.triggered.connect(
                self.open_selected_directory_entry
            )

        menu.exec(
            self.directory_table.mapToGlobal(position)
        )

        menu.deleteLater()

    def refresh_path_table(self):
        if not hasattr(self, "path_table"):
            return

        paths = self.context.search_paths

        self.path_table.setRowCount(len(paths))

        for row, directory in enumerate(paths):
            priority_item = QTableWidgetItem(
                str(row + 1)
            )
            directory_item = QTableWidgetItem(directory)
            status_item = QTableWidgetItem(
                self.directory_status(directory)
            )

            self.path_table.setItem(
                row,
                0,
                priority_item,
            )
            self.path_table.setItem(
                row,
                1,
                directory_item,
            )
            self.path_table.setItem(
                row,
                2,
                status_item,
            )

        self.path_table.resizeRowsToContents()

    def directory_status(self, directory):
        if not os.path.isdir(directory):
            return "Missing"

        if not os.access(directory, os.R_OK):
            return "Inaccessible"

        return "OK"

    def selected_path_row(self):
        if not hasattr(self, "path_table"):
            return None

        selected = self.path_table.selectedItems()

        if not selected:
            return None

        row = selected[0].row()

        if row < 0 or row >= len(
            self.context.search_paths
        ):
            return None

        return row

    def select_path_row(self, row):
        if not hasattr(self, "path_table"):
            return

        if row < 0 or row >= self.path_table.rowCount():
            return

        self.path_table.selectRow(row)

    def update_function_diagnostics(self):
        if not hasattr(self, "path_feedback_label"):
            return

        if hasattr(self, "path_summary_label"):
            self.path_summary_label.setText(
                "Function search order: built-ins, "
                "same-file/local functions, core library, "
                "current folder "
                f"({self.context.current_working_directory}), "
                "then external paths in the order listed below."
            )

        try:
            locations = (
                self.context
                .function_resolver
                .function_locations()
            )
        except Exception as error:
            self.path_feedback_label.setText(
                f"Unable to scan function paths: {error}"
            )
            return

        duplicate_lines = []
        builtin_conflicts = []

        for name, function_locations in sorted(
            locations.items()
        ):
            if self.context.functions.is_builtin(name):
                builtin_conflicts.append(
                    f"{name} in "
                    f"{function_locations[0]['path']}"
                )
                continue

            directories = {
                location["directory"]
                for location in function_locations
            }

            if len(directories) <= 1:
                continue

            winner = function_locations[0]

            duplicate_lines.append(
                f"{name}: {winner['scope']} wins "
                f"({winner['path']})"
            )

        messages = []

        if builtin_conflicts:
            messages.append(
                "Built-in conflicts detected: "
                + "; ".join(builtin_conflicts[:3])
            )

        if duplicate_lines:
            messages.append(
                "Duplicate function names: "
                + "; ".join(duplicate_lines[:4])
            )

        if not messages:
            messages.append(
                "No duplicate function names detected "
                "across the core library, current folder, "
                "and external paths."
            )

        self.path_feedback_label.setText(
            "\n".join(messages)
        )

    def setup_workspace_panel(self):
        dock = QDockWidget("Workspace", self)

        self.workspace_dock = dock

        dock.setStyleSheet("""
            QDockWidget {
                color: #D4D4D4;
            }
            QDockWidget::title {
                background-color: #252526;
            }
        """)

        self.workspace_table = QTableWidget()

        self.workspace_table.setColumnCount(4)

        self.workspace_table.setHorizontalHeaderLabels(
            [
                "Name",
                "Type",
                "Size",
                "Value",
            ]
        )

        dock.setWidget(self.workspace_table)

        self.addDockWidget(
            Qt.RightDockWidgetArea,
            dock,
        )

        self.workspace_table.setAlternatingRowColors(
            True
        )

        self.workspace_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.workspace_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        header = (
            self.workspace_table.horizontalHeader()
        )

        header.setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.workspace_table.cellDoubleClicked.connect(
            self.inspect_variable
        )

    def refresh_workspace(self):
        variables = {
            name: value
            for name, value in (
                self.context.variables.items()
            )
            if name not in RESERVED_CONSTANTS
        }

        self.workspace_table.setRowCount(
            len(variables)
        )

        for row, (name, value) in enumerate(
            variables.items()
        ):
            # Name
            self.workspace_table.setItem(
                row,
                0,
                QTableWidgetItem(name),
            )

            # Type
            type_name = type(value).__name__

            if is_lti_model(value):
                type_name = f"{value.model_type} model"

            if isinstance(value, SymbolicValue):
                type_name = "sym"

            if isinstance(value, FunctionHandle):
                type_name = "function_handle"

            if isinstance(value, dict):
                type_name = "struct"

            self.workspace_table.setItem(
                row,
                1,
                QTableWidgetItem(type_name),
            )

            # Size
            size_text = self.get_size_text(value)

            self.workspace_table.setItem(
                row,
                2,
                QTableWidgetItem(size_text),
            )

            # Value Preview
            preview = self.get_preview_text(value)

            self.workspace_table.setItem(
                row,
                3,
                QTableWidgetItem(preview),
            )

        self.workspace_table.resizeColumnsToContents()

    def get_size_text(self, value):
        try:
            import numpy as np

            if isinstance(value, np.ndarray):
                return "x".join(
                    str(x)
                    for x in value.shape
                )

        except Exception:
            pass

        if isinstance(value, str):
            return str(len(value))

        return "1x1"

    def get_preview_text(self, value):
        if is_lti_model(value):
            return value.workspace_preview()

        text = format_value(
            value,
            self.context.display_format,
        )

        if len(text) > 40:
            text = text[:40] + "..."

        return text

    def inspect_variable(self, row, column):
        name_item = (
            self.workspace_table.item(row, 0)
        )

        if not name_item:
            return

        name = name_item.text()

        value = self.context.variables.get(
            name
        )

        dock = QDockWidget(
            f"Variable: {name}",
            self,
        )

        editor = VariableEditor(
            name,
            value,
            self.update_variable,
            self.context.display_format,
        )

        dock.setWidget(editor)

        self.addDockWidget(
            Qt.RightDockWidgetArea,
            dock,
        )

    def update_variable(self, name, value):
        self.context.variables[name] = value

        self.refresh_workspace()

    def clear_workspace(self):
        self.context.clear()

        self.refresh_workspace()

        self.console.appendPlainText(
            "Workspace cleared"
        )

    def create_new_tab(
        self,
        content="",
        filename="Untitled"
    ):
        editor = CodeEditor()

        editor.breakpoint_toggled.connect(
            lambda line, enabled, e=editor:
            self.on_editor_breakpoint_toggled(
                e,
                line,
                enabled,
            )
        )

        editor.file_path = None

        font = QFont("Consolas", 12)

        editor.setFont(font)

        editor.setPlainText(content)

        editor.highlighter = (
            MathToolSyntaxHighlighter(
                editor.document(),
                self.preferences["theme"],
            )
        )

        self.apply_editor_preferences(editor)

        index = self.tabs.addTab(
            editor,
            filename
        )

        self.tabs.setTabToolTip(
            index,
            filename,
        )

        self.tabs.setCurrentIndex(index)

        editor.document().modificationChanged.connect(
            lambda changed, e=editor:
            self.update_tab_title(e, changed)
        )

        editor.document().setModified(False)

        return editor

    def current_editor(self):
        return self.tabs.currentWidget()

    def invoke_editor_action(self, action_name):
        editor = self.current_editor()

        if editor is None:
            return

        action = getattr(editor, action_name, None)

        if action is None:
            return

        action()

    def close_current_tab(self):
        self.close_tab(
            self.tabs.currentIndex()
        )

    def editor_display_name(self, editor):
        if getattr(editor, "file_path", None):
            return os.path.basename(editor.file_path)

        index = self.tabs.indexOf(editor)

        if index != -1:
            title = self.tabs.tabText(index)

            if title.endswith("*"):
                title = title[:-1]

            if title:
                return title

        return "Untitled"

    def set_editor_tab_title(self, editor):
        index = self.tabs.indexOf(editor)

        if index == -1:
            return

        title = self.editor_display_name(editor)

        if editor.document().isModified():
            title = f"{title}*"

        self.tabs.setTabText(
            index,
            title,
        )

        tooltip = (
            editor.file_path
            if getattr(editor, "file_path", None)
            else "Unsaved script"
        )

        self.tabs.setTabToolTip(
            index,
            tooltip,
        )

    def unsaved_editors(self):
        return [
            editor
            for editor in self.all_code_editors()
            if editor.document().isModified()
        ]

    def prompt_unsaved_changes(self, editors, action):
        names = [
            self.editor_display_name(editor)
            for editor in editors
        ]

        message_box = QMessageBox(self)
        message_box.setIcon(
            QMessageBox.Icon.Warning
        )
        message_box.setWindowTitle(
            "Unsaved Changes"
        )

        if action == "quit":
            message_box.setText(
                "Save changes before quitting MathTool?"
            )
        else:
            message_box.setText(
                f"Save changes to {names[0]} before closing?"
            )

        if len(names) == 1:
            detail = f"Unsaved script: {names[0]}"
        else:
            visible_names = names[:5]
            detail = (
                "Unsaved scripts:\n"
                + "\n".join(
                    f"- {name}"
                    for name in visible_names
                )
            )

            remaining_count = len(names) - len(visible_names)

            if remaining_count:
                detail += (
                    f"\n- and {remaining_count} more"
                )

        message_box.setInformativeText(
            detail
            + "\n\nChoose Save to keep your changes, "
            "Discard to close without saving, or "
            "Cancel to keep editing."
        )

        save_button = message_box.addButton(
            "Save",
            QMessageBox.ButtonRole.AcceptRole,
        )
        discard_button = message_box.addButton(
            "Discard",
            QMessageBox.ButtonRole.DestructiveRole,
        )
        cancel_button = message_box.addButton(
            "Cancel",
            QMessageBox.ButtonRole.RejectRole,
        )

        message_box.setDefaultButton(save_button)
        message_box.setEscapeButton(cancel_button)

        message_box.exec()

        clicked_button = message_box.clickedButton()

        if clicked_button == save_button:
            return "save"

        if clicked_button == discard_button:
            return "discard"

        return "cancel"

    def confirm_close_editors(self, editors, action):
        dirty_editors = [
            editor
            for editor in editors
            if (
                editor is not None
                and editor.document().isModified()
            )
        ]

        if not dirty_editors:
            return True

        for editor in dirty_editors:
            self.tabs.setCurrentWidget(editor)
            self.set_editor_tab_title(editor)

        response = self.prompt_unsaved_changes(
            dirty_editors,
            action,
        )

        if response == "cancel":
            if hasattr(self, "status_label"):
                self.status_label.setText(
                    "Close canceled"
                )

            return False

        if response == "discard":
            return True

        for editor in dirty_editors:
            self.tabs.setCurrentWidget(editor)

            if not self.save_editor(editor):
                if hasattr(self, "status_label"):
                    self.status_label.setText(
                        "Close canceled"
                    )

                return False

        return True

    def close_tab(self, index):
        if index < 0 or index >= self.tabs.count():
            return

        editor = self.tabs.widget(index)

        if not self.confirm_close_editors(
            [editor],
            "close",
        ):
            return

        self.tabs.removeTab(index)

        if self.tabs.count() == 0:
            self.create_new_tab()

    def can_reuse_current_untitled_editor(self):
        editor = self.current_editor()

        return (
            editor is not None
            and self.tabs.count() == 1
            and not getattr(editor, "file_path", None)
            and not editor.document().isModified()
            and not editor.toPlainText()
        )

    def new_file(self):
        self.create_new_tab()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            self.context.current_working_directory,
            "MathTool Files (*.m);;All Files (*)",
        )

        if not path:
            return

        self.open_file_path(path)

    def open_file_path(self, path):
        if not os.path.isfile(path):
            QMessageBox.warning(
                self,
                "Open File",
                f"File does not exist: {path}",
            )

            return

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:
            content = f.read()

        filename = os.path.basename(path)

        if self.can_reuse_current_untitled_editor():
            editor = self.current_editor()
            editor.setPlainText(content)
        else:
            editor = self.create_new_tab(
                content,
                filename
            )

        editor.file_path = path
        editor.document().setModified(False)
        self.set_editor_tab_title(editor)

    def save_file(self):
        return self.save_editor(
            self.current_editor()
        )

    def save_file_as(self):
        return self.save_editor_as(
            self.current_editor()
        )

    def save_editor(self, editor):
        if editor is None:
            return False

        if not getattr(editor, "file_path", None):
            return self.save_editor_as(editor)

        try:
            with open(
                editor.file_path,
                "w",
                encoding="utf-8"
            ) as f:
                f.write(
                    editor.toPlainText()
                )
        except OSError as error:
            QMessageBox.critical(
                self,
                "Save File",
                f"Could not save file:\n{error}",
            )

            return False

        self.console.appendPlainText(
            f"Saved: {editor.file_path}"
        )

        editor.document().setModified(False)
        self.set_editor_tab_title(editor)

        if hasattr(self, "status_label"):
            self.status_label.setText(
                f"Saved {self.editor_display_name(editor)}"
            )

        return True

    def save_editor_as(self, editor):
        if editor is None:
            return False

        suggested_path = (
            editor.file_path
            if getattr(editor, "file_path", None)
            else os.path.join(
                self.context.current_working_directory,
                self.editor_display_name(editor),
            )
        )

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            suggested_path,
            "MathTool Files (*.m);;All Files (*)",
        )

        if not path:
            return False

        try:
            with open(
                path,
                "w",
                encoding="utf-8"
            ) as f:
                f.write(
                    editor.toPlainText()
                )
        except OSError as error:
            QMessageBox.critical(
                self,
                "Save File As",
                f"Could not save file:\n{error}",
            )

            return False

        editor.file_path = path

        self.console.appendPlainText(
            f"Saved: {path}"
        )

        editor.document().setModified(False)
        self.set_editor_tab_title(editor)

        if hasattr(self, "status_label"):
            self.status_label.setText(
                f"Saved {self.editor_display_name(editor)}"
            )

        return True

    def update_tab_title(
        self,
        editor,
        changed
    ):
        self.set_editor_tab_title(editor)

    def closeEvent(self, event):
        if self.confirm_close_editors(
            self.unsaved_editors(),
            "quit",
        ):
            event.accept()
            return

        event.ignore()

    def setup_command_window(self):
        dock = QDockWidget(
            "Command Window",
            self
        )

        self.command_dock = dock

        dock.setStyleSheet("""
            QDockWidget {
                color: #D4D4D4;
            }
            QDockWidget::title {
                background-color: #252526;
            }
        """)

        self.command_window = (
            CommandWindow(
                self.execute_repl_code,
                format_callback=(
                    lambda value: format_value(
                        value,
                        self.context.display_format,
                    )
                ),
                suffix_callback=(
                    lambda: output_suffix(
                        self.context.display_format
                    )
                ),
            )
        )

        dock.setWidget(
            self.command_window
        )

        self.addDockWidget(
            Qt.BottomDockWidgetArea,
            dock
        )

    def setup_documentation_panel(self):
        dock = QDockWidget(
            "Documentation",
            self,
        )

        self.documentation_dock = dock

        self.documentation_panel = DocumentationPanel(
            self.context.help_database,
            self,
        )

        dock.setWidget(self.documentation_panel)

        self.addDockWidget(
            Qt.RightDockWidgetArea,
            dock,
        )

        dock.hide()

    def execute_repl_code(self, source):
        if (
            self.execution_thread
            and self.execution_thread.isRunning()
        ):
            return "Execution already running"        

        if not hasattr(self, "session"):
            self.session = MathToolSession(
                context=self.context
            )
            self.interpreter = self.session.interpreter
            self.semantic = self.session.semantic

        result = self.session.execute(
            source,
            allow_commands=True,
            allow_script_commands=True,
        )

        if hasattr(self, "update_display_format_status"):
            self.update_display_format_status()

        if result.should_exit:
            self.close()
            return None

        if result.clear_output:
            self.command_window.clear()
            return None

        if result.command in {"help", "doc"}:
            self.show_documentation_panel(
                result.help_topic
            )

            if result.command == "doc":
                return None

        if result.workspace_changed:
            if hasattr(self, "refresh_workspace"):
                self.refresh_workspace()

            if hasattr(self, "refresh_variable_editors"):
                self.refresh_variable_editors()

            if hasattr(self, "update_runtime_path_ui"):
                self.update_runtime_path_ui()

        return result.value

    def route_output(self, text):
        text = str(text)

        # REPL active
        if (
            hasattr(self, "command_window")
            and self.command_window.hasFocus()
        ):
            self.insert_output_text(
                self.command_window,
                text
            )

        else:
            self.insert_output_text(
                self.console,
                text
            )

    def insert_output_text(self, widget, text, message_type=None):
        widget.moveCursor(QTextCursor.End)

        cursor = widget.textCursor()

        text_format = self.output_text_format(
            text,
            message_type,
        )

        if text_format is None:
            text_format = self.normal_text_format(
                widget
            )

        cursor.insertText(text, text_format)

        widget.setTextCursor(cursor)
        self.reset_text_format(widget)

    def normal_text_format(self, widget):
        text_format = QTextCharFormat()

        color = "#D4D4D4"

        if hasattr(self, "preferences"):
            colors = theme_for_preferences(
                self.preferences
            )
            color = colors["editor_foreground"]

        text_format.setForeground(
            QColor(color)
        )

        return text_format

    def reset_text_format(self, widget):
        text_format = self.normal_text_format(widget)

        cursor = widget.textCursor()
        cursor.setCharFormat(text_format)

        widget.setTextCursor(cursor)
        widget.setCurrentCharFormat(text_format)

    def output_text_format(self, text, message_type=None):
        stripped = str(text).lstrip()

        if (
            message_type == "warning"
            or stripped.startswith("Warning:")
        ):
            text_format = QTextCharFormat()
            text_format.setForeground(
                QColor("#FFA500")
            )
            return text_format

        if (
            message_type == "error"
            or stripped.startswith("Error:")
        ):
            text_format = QTextCharFormat()
            text_format.setForeground(
                QColor("#FF4D4D")
            )
            return text_format

        return None

    def show_output_context_menu(self, position):
        menu = self.console.createStandardContextMenu()

        menu.addSeparator()

        clear_action = menu.addAction("Clear Output")

        clear_action.triggered.connect(
            self.console.clear
        )

        menu.exec(
            self.console.mapToGlobal(position)
        )

        menu.deleteLater()

    def on_editor_breakpoint_toggled(
        self,
        editor,
        line,
        enabled,
    ):
        active_debug_editor = (
            self.execution_editor
            if self.debugger.enabled
            and self.execution_editor is not None
            else self.current_editor()
        )

        if editor is not active_debug_editor:
            return

        if enabled:
            self.debugger.add_breakpoint(line)

            message = f"Breakpoint added at line {line}"

        else:
            self.debugger.remove_breakpoint(line)

            message = f"Breakpoint removed at line {line}"

        if hasattr(self, "status_label"):
            self.status_label.setText(message)

    def sync_breakpoints(self, *_):
        editor = (
            self.execution_editor
            if self.debugger.enabled
            and self.execution_editor is not None
            else self.current_editor()
        )

        lines = (
            editor.breakpoints
            if editor is not None
            and hasattr(editor, "breakpoints")
            else set()
        )

        if hasattr(self.debugger, "set_breakpoints"):
            self.debugger.set_breakpoints(lines)

            return

        for line in list(self.debugger.breakpoints):
            self.debugger.remove_breakpoint(line)

        for line in lines:
            self.debugger.add_breakpoint(line)

    def clear_debug_highlights(self):
        if not hasattr(self, "tabs"):
            return

        for index in range(self.tabs.count()):
            editor = self.tabs.widget(index)

            if hasattr(editor, "highlight_debug_line"):
                editor.highlight_debug_line(None)

        if hasattr(self, "status_label"):
            self.status_label.setText("Ready")

    def add_breakpoint_dialog(self):
        line, ok = (
            QInputDialog.getInt(
                self,
                "Add Breakpoint",
                "Line number:",
                1,
                1,
                100000,
            )
        )

        if ok:
            editor = self.current_editor()

            if (
                editor is not None
                and hasattr(editor, "set_breakpoint")
            ):
                editor.set_breakpoint(line, True)

                self.sync_breakpoints()

            else:
                self.debugger.add_breakpoint(
                    line
                )

            self.console.appendPlainText(
                f"Breakpoint added at line {line}"
            )

    def setup_status_bar(self):
        """Setup status bar at the bottom"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #252526;
                color: #D4D4D4;
                border-top: 1px solid #3E3E42;
            }
        """)
        
        status_label = QLabel("Ready")
        status_bar.addWidget(status_label)
        
        self.status_label = status_label

        cwd_label = QLabel()
        status_bar.addPermanentWidget(cwd_label)

        self.cwd_label = cwd_label

        format_label = QLabel()
        status_bar.addPermanentWidget(format_label)

        self.format_label = format_label

        self.update_display_format_status()

        self.update_working_directory_status()

    def update_display_format_status(self):
        if not hasattr(self, "format_label"):
            return

        settings = self.context.display_format.settings

        self.format_label.setText(
            f"Format: {settings.numeric_format.upper()} / "
            f"{settings.spacing_mode.upper()}"
        )

    def stop_execution(self):
        self.debugger.stop_session()

        if self.execution_worker:
            self.execution_worker.cancel()

            self.console.appendPlainText(
                "Execution cancelled"
            )

        self.clear_debug_highlights()

        self.run_button.setEnabled(True)

        if hasattr(self, "debug_button"):
            self.debug_button.setEnabled(True)
