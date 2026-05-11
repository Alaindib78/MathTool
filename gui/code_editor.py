from PySide6.QtWidgets import (
    QPlainTextEdit,
    QTextEdit,
)

from PySide6.QtGui import (
    QColor,
    QTextFormat,
    QTextCursor,
)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTextEdit


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()

        self.cursorPositionChanged.connect(
            self.highlight_current_line
        )

        self.highlight_current_line()

    def highlight_current_line(self):
        extra_selections = []

        if not self.isReadOnly():
            selection = (
                QTextEdit.ExtraSelection()
            )

            line_color = QColor(
                "#2A2D2E"
            )

            selection.format.setBackground(
                line_color
            )

            selection.format.setProperty(
                QTextFormat.FullWidthSelection,
                True,
            )

            selection.cursor = (
                self.textCursor()
            )

            selection.cursor.clearSelection()

            extra_selections.append(
                selection
            )

        self.setExtraSelections(
            extra_selections
        )

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

        if event.key() in (
            Qt.Key_Return,
            Qt.Key_Enter,
        ):
            cursor = self.textCursor()

            cursor.movePosition(
                QTextCursor.Up
            )

            previous_line = (
                cursor.block().text()
            )

            indentation = ""

            for char in previous_line:
                if char in (" ", "\t"):
                    indentation += char
                else:
                    break

            if (
                previous_line.strip().startswith("if")
                or previous_line.strip().startswith("for")
                or previous_line.strip().startswith("while")
                or previous_line.strip().startswith("function")
            ):
                indentation += "    "

            self.insertPlainText(
                indentation
            )

    def match_brackets(self):
        pass