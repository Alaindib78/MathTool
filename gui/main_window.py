from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QToolBar,
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
from core.runtime.context import RuntimeContext
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