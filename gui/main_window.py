import ast
import os
from tkinter import font

from PySide6.QtWidgets import (
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
    QLabel,
    QStatusBar,
)

from PySide6.QtGui import (
    QAction,
    QKeySequence,
    QIcon,
    QFont,
    QColor,
)

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QSizePolicy
from matplotlib import text

from core.lexer import lexer
from core.lexer.lexer import Lexer
from core.parser.parser import Parser
from core.semantic.semantic_analyzer import (
    SemanticAnalyzer
)
from core.interpreter.interpreter import (
    Interpreter
)
from core.runtime.context import RESERVED_CONSTANTS, RuntimeContext 
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MathTool")

        self.resize(1400, 900)

        self.context = RuntimeContext()

        self.context.output_callback = (
            self.route_output
        )

        self.debugger = Debugger()

        self.context.debugger = (
            self.debugger
        )

        self.debugger.pause_callback = (
            self.on_debug_pause
        )

        self.interpreter = Interpreter(
            self.context
        )

        self.semantic = SemanticAnalyzer()

        # Apply modern styling
        self.apply_stylesheet()

        self.setup_ui()

        self.setup_workspace_panel()

        self.setup_command_window()

        self.setup_toolbar()

        self.setup_menu()

        self.setup_status_bar()

    def apply_stylesheet(self):
        """Apply a modern dark theme stylesheet"""
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
            margin: 4px 0px;
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
        self.tabs.tabCloseRequested.connect(
            self.close_tab
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
        run_button = QPushButton("▶ Run")
        run_button.setStyleSheet("""
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
        run_button.clicked.connect(self.run_code)
        toolbar.addWidget(run_button)

        toolbar.addSeparator()

        # File operations
        new_button = QPushButton("+ New")
        new_button.setObjectName("secondaryButton")
        new_button.clicked.connect(self.new_file)
        toolbar.addWidget(new_button)

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

    def run_code(self):
        editor = self.current_editor()

        if editor is None:
            return

        source = editor.toPlainText()

        try:
            lexer = Lexer(source)

            tokens = lexer.tokenize()

            parser = Parser(tokens)

            ast = parser.parse()

            self.semantic.analyze(ast)

            result = (
                self.interpreter.evaluate(ast)
            )

            self.refresh_workspace()

            if result is not None:
                self.console.appendPlainText(
                    str(result)
                )

        except Exception as e:
            self.console.appendPlainText(
                f"Error: {str(e)}"
            )

    def write_output(self, text):
        self.console.appendPlainText(str(text))

    def debug_continue(self):
        self.debugger.continue_execution()

    def debug_step(self):
        self.debugger.step()

    def on_debug_pause(self, node):
        line = getattr(node, "line", None)

        if line is None:
            return

        editor = self.current_editor()

        if editor is None:
            return

        block = (
            editor.document()
            .findBlockByLineNumber(line - 1)
        )

        cursor = editor.textCursor()

        cursor.setPosition(
            block.position()
        )

        editor.setTextCursor(cursor)

        editor.setFocus()

    def setup_menu(self):
        menu = self.menuBar()

        # File Menu
        file_menu = menu.addMenu("File")

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

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menu.addMenu("Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        edit_menu.addAction(select_all_action)

        # Run Menu
        run_menu = menu.addMenu("Run")

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
        debug_menu = menu.addMenu("Debug")

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

        # Tools Menu
        tools_menu = menu.addMenu("Tools")

        options_action = QAction("Options", self)
        tools_menu.addAction(options_action)

        # Help Menu
        help_menu = menu.addMenu("Help")

        about_action = QAction("About MathTool", self)
        help_menu.addAction(about_action)

        documentation_action = QAction(
            "Documentation",
            self
        )
        help_menu.addAction(documentation_action)

    def setup_workspace_panel(self):
        dock = QDockWidget("Workspace", self)
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
        text = str(value)

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

        editor.file_path = None

        font = QFont("Consolas", 12)

        editor.setFont(font)

        editor.setPlainText(content)

        highlighter = (
            MathToolSyntaxHighlighter(
                editor.document()
            )
        )

        index = self.tabs.addTab(
            editor,
            filename
        )

        self.tabs.setCurrentIndex(index)

        editor.document().modificationChanged.connect(
            lambda changed, e=editor:
            self.update_tab_title(e, changed)
        )

        return editor

    def current_editor(self):
        return self.tabs.currentWidget()

    def close_tab(self, index):
        if self.tabs.count() == 1:
            return

        editor = self.tabs.widget(index)

        if editor.document().isModified():
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                "This tab has unsaved changes. "
                "Close anyway?",
            )

            if result != QMessageBox.Yes:
                return

        self.tabs.removeTab(index)

    def new_file(self):
        self.create_new_tab()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "MathTool Files (*.m);;All Files (*)",
        )

        if not path:
            return

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:
            content = f.read()

        filename = os.path.basename(path)

        editor = self.create_new_tab(
            content,
            filename
        )

        editor.file_path = path

    def save_file(self):
        editor = self.current_editor()

        if editor is None:
            return

        if not editor.file_path:
            self.save_file_as()
            return

        with open(
            editor.file_path,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(
                editor.toPlainText()
            )

        self.console.appendPlainText(
            f"Saved: {editor.file_path}"
        )

        editor.document().setModified(False)

    def save_file_as(self):
        editor = self.current_editor()

        if editor is None:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            "",
            "MathTool Files (*.m);;All Files (*)",
        )

        if not path:
            return

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(
                editor.toPlainText()
            )

        editor.file_path = path

        filename = os.path.basename(path)

        index = self.tabs.currentIndex()

        self.tabs.setTabText(
            index,
            filename
        )

        self.console.appendPlainText(
            f"Saved: {path}"
        )

        editor.document().setModified(False)

    def update_tab_title(
        self,
        editor,
        changed
    ):
        index = self.tabs.indexOf(editor)

        if index == -1:
            return

        title = self.tabs.tabText(index)

        if changed:
            if not title.endswith("*"):
                title += "*"
        else:
            title = title.rstrip("*")

        self.tabs.setTabText(
            index,
            title
        )

    def setup_command_window(self):
        dock = QDockWidget(
            "Command Window",
            self
        )

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
                self.execute_repl_code
            )
        )

        dock.setWidget(
            self.command_window
        )

        self.addDockWidget(
            Qt.BottomDockWidgetArea,
            dock
        )

    def execute_repl_code(self, source):
        if source.strip() in (
            "exit",
            "quit",
        ):
            self.close()
            return None

        if source.strip() == "clear":
            self.clear_workspace()
            return None

        if source.strip() == "clc":
            self.command_window.clear()

            self.command_window.insert_prompt()

            return None

        lexer = Lexer(source)

        tokens = lexer.tokenize()

        parser = Parser(tokens)

        ast = parser.parse()

        self.semantic.analyze(ast)

        result = (
            self.interpreter.evaluate(ast)
        )

        self.refresh_workspace()

        return result

    def route_output(self, text):
        text = str(text)

        # REPL active
        if (
            hasattr(self, "command_window")
            and self.command_window.hasFocus()
        ):
            self.command_window.insertPlainText(
                text
            )

            self.command_window.insertPlainText(
                "\n"
            )

        else:
            self.console.appendPlainText(text)

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