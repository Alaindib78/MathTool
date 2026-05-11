import ast
import os
from tkinter import font

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
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
)

from PySide6.QtGui import QAction, QKeySequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtGui import QAction
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MathTool")

        self.resize(1200, 800)

        self.context = RuntimeContext()

        self.context.output_callback = (
            self.route_output
        )

        self.interpreter = Interpreter(
            self.context
        )

        self.semantic = SemanticAnalyzer()

        self.setup_ui()

        self.setup_workspace_panel()

        self.setup_command_window()

        self.setup_toolbar()

        self.setup_menu()



    def setup_ui(self):
        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        layout = QVBoxLayout()

        central_widget.setLayout(layout)

        # ---------------------------------
        # Splitter
        # ---------------------------------

        splitter = QSplitter(
            Qt.Vertical
        )

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

        self.console = QPlainTextEdit()

        self.console.setReadOnly(True)

        font = QFont("Consolas", 12)
        self.console.setFont(font)

        self.console.setStyleSheet(
            """
            background-color: #1E1E1E;
            color: #D4D4D4;
            border: none;
            """
        )

        splitter.addWidget(self.console)

        splitter.setSizes([600, 200])

        # ---------------------------------
        # Run Button
        # ---------------------------------

        run_button = QPushButton("Run")

        run_button.clicked.connect(
            self.run_code
        )

        layout.addWidget(run_button)

    def setup_toolbar(self):
        toolbar = QToolBar()

        self.addToolBar(toolbar)

        run_button = QPushButton("Run")

        run_button.clicked.connect(
            self.run_code
        )

        toolbar.addWidget(run_button)

        clear_workspace_button = QPushButton(
            "Clear Workspace"
        )

        clear_workspace_button.clicked.connect(
            self.clear_workspace
        )

        toolbar.addWidget(
            clear_workspace_button
        )

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
                str(e)
            )
    def write_output(self, text):
        self.console.appendPlainText(str(text))

    def setup_menu(self):
        menu = self.menuBar()

        file_menu = menu.addMenu("File")

        run_action = QAction("Run", self)

        run_action.triggered.connect(
            self.run_code
        )

        file_menu.addAction(run_action)

        new_action = QAction("New", self)

        new_action.triggered.connect(
            self.new_file
        )

        file_menu.addAction(new_action)

        open_action = QAction("Open", self)

        open_action.triggered.connect(
            self.open_file
        )

        file_menu.addAction(open_action)

        save_action = QAction("Save", self)

        save_action.triggered.connect(
            self.save_file
        )

        file_menu.addAction(save_action)

        save_as_action = QAction(
            "Save As",
            self
        )

        save_as_action.triggered.connect(
            self.save_file_as
        )

        file_menu.addAction(save_as_action)

        new_action.setShortcut(
            QKeySequence.New
        )

        open_action.setShortcut(
            QKeySequence.Open
        )

        save_action.setShortcut(
            QKeySequence.Save
        )

        save_as_action.setShortcut(
            QKeySequence.SaveAs
        )

    def setup_workspace_panel(self):
        dock = QDockWidget(
            "Workspace",
            self
        )

        self.workspace_table = (
            QTableWidget()
        )

        self.workspace_table.setColumnCount(4)

        self.workspace_table.setHorizontalHeaderLabels(
            [
                "Name",
                "Type",
                "Size",
                "Value",
            ]
        )

        dock.setWidget(
            self.workspace_table
        )

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
            # -----------------------------
            # Name
            # -----------------------------

            self.workspace_table.setItem(
                row,
                0,
                QTableWidgetItem(name),
            )

            # -----------------------------
            # Type
            # -----------------------------

            type_name = type(value).__name__

            self.workspace_table.setItem(
                row,
                1,
                QTableWidgetItem(type_name),
            )

            # -----------------------------
            # Size
            # -----------------------------

            size_text = self.get_size_text(
                value
            )

            self.workspace_table.setItem(
                row,
                2,
                QTableWidgetItem(size_text),
            )

            # -----------------------------
            # Value Preview
            # -----------------------------

            preview = self.get_preview_text(
                value
            )

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

        self.console.appendPlainText(
            f"\n{name} =\n{value}\n"
        )

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

        editor.setStyleSheet(
            """
            background-color: #1E1E1E;
            color: #D4D4D4;
            border: none;
            """
        )

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

    def setup_command_window(self):
        dock = QDockWidget(
            "Command Window",
            self
        )

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