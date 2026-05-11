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
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtGui import QAction
from matplotlib import text

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MathTool")

        self.resize(1200, 800)

        self.context = RuntimeContext()

        self.context.output_callback = (
            self.write_output
        )

        self.interpreter = Interpreter(
            self.context
        )

        self.semantic = SemanticAnalyzer()

        self.setup_ui()

        self.setup_workspace_panel()

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
        # Code Editor
        # ---------------------------------

        self.editor = CodeEditor()

        self.highlighter = (
            MathToolSyntaxHighlighter(
                self.editor.document()
            )
        )

        self.editor.setStyleSheet(
            """
            background-color: #1E1E1E;
            color: #D4D4D4;
            border: none;
            """
        )

        self.editor.setPlaceholderText(
            "Write MathTool code here..."
        )
        font = QFont("Consolas", 12)

        self.editor.setFont(font)

        splitter.addWidget(self.editor)

        # ---------------------------------
        # Output Console
        # ---------------------------------

        self.console = QPlainTextEdit()

        self.console.setReadOnly(True)

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
        source = self.editor.toPlainText()

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