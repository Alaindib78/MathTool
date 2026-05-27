from email.mime import text

from PySide6.QtWidgets import (
    QPlainTextEdit,
)

from PySide6.QtGui import (
    QTextCursor,
    QFont,
    QColor,
    QTextCharFormat,
)

from PySide6.QtCore import Qt

from core.runtime.formatting import format_value, output_suffix


class CommandWindow(QPlainTextEdit):
    def __init__(
        self,
        execute_callback,
        format_callback=None,
        suffix_callback=None,
    ):
        super().__init__()

        self.execute_callback = (
            execute_callback
        )

        self.format_callback = (
            format_callback
            if format_callback is not None
            else format_value
        )

        self.suffix_callback = (
            suffix_callback
            if suffix_callback is not None
            else output_suffix
        )

        self.history = []

        self.history_index = -1

        self.prompt = ">> "

        self.normal_text_color = QColor(
            "#D4D4D4"
        )

        self.setFont(
            QFont("Consolas", 11)
        )

        self.setStyleSheet(
            """
            background-color: #1E1E1E;
            color: #D4D4D4;
            border: none;
            """
        )

        self.prompt_position = 0

        self.insert_prompt()

        self.setUndoRedoEnabled(False)

    # ---------------------------------
    # Key Handling
    # ---------------------------------

    def keyPressEvent(self, event):
        cursor = self.textCursor()

        # Prevent editing before prompt
        if (
            cursor.position()
            < self.prompt_position
        ):
            cursor.movePosition(
                QTextCursor.End
            )

            self.setTextCursor(cursor)

            return

        key = event.key()

        # ---------------------------------
        # Enter executes command
        # ---------------------------------

        if key in (
            Qt.Key_Return,
            Qt.Key_Enter,
        ):
            self.execute_current_line()
            return

        # ---------------------------------
        # History navigation
        # ---------------------------------

        if key == Qt.Key_Up:
            self.history_up()
            return

        if key == Qt.Key_Down:
            self.history_down()
            return

        # ---------------------------------
        # Prevent editing old content
        # ---------------------------------

        cursor = self.textCursor()

        current_block = (
            cursor.block().text()
        )

        if (
            cursor.positionInBlock()
            < len(self.prompt)
        ):
            cursor.movePosition(
                QTextCursor.End
            )

            self.setTextCursor(cursor)

        if key == Qt.Key_Backspace:
            cursor = self.textCursor()

            if (
                cursor.position()
                <= self.prompt_position
            ):
                return
            
        if key == Qt.Key_Left:
            cursor = self.textCursor()

            if (
                cursor.position()
                <= self.prompt_position
            ):
                return
            
        if key == Qt.Key_Home:
            cursor = self.textCursor()

            cursor.setPosition(
                self.prompt_position
            )

            self.setTextCursor(cursor)

            return
        
        # Always keep cursor at end
        cursor = self.textCursor()

        if cursor.position() < self.prompt_position:
            cursor.movePosition(
                QTextCursor.End
            )

            self.setTextCursor(cursor)

        super().keyPressEvent(event)

    # ---------------------------------
    # Command Execution
    # ---------------------------------

    def execute_current_line(self):
        self.reset_text_format()

        cursor = self.textCursor()

        cursor.movePosition(
            QTextCursor.End
        )

        self.setTextCursor(cursor)

        # ---------------------------------
        # Extract current command
        # ---------------------------------

        text = self.toPlainText()

        lines = text.splitlines()

        if not lines:
            return

        current_line = lines[-1]

        if not current_line.startswith(
            self.prompt
        ):
            return

        command = current_line[
            len(self.prompt):
        ].strip()

        # Move to next line after command
        self.insert_normal_text("\n")

        # ---------------------------------
        # Execute command
        # ---------------------------------

        if command:
            self.history.append(command)

            self.history_index = (
                len(self.history)
            )

            try:
                result = (
                    self.execute_callback(
                        command
                    )
                )

                if result is not None:
                    self.insert_normal_text(
                        self.format_callback(result)
                    )

                    self.insert_normal_text(
                        self.suffix_callback()
                    )

            except Exception as e:
                if not getattr(
                    e,
                    "already_reported",
                    False,
                ):
                    self.insert_output_text(
                        str(e) + "\n",
                        "error",
                    )

        # ---------------------------------
        # Insert next prompt
        # ---------------------------------

        self.insert_prompt()

        cursor = self.textCursor()

        cursor.movePosition(
            QTextCursor.End
        )

        self.setTextCursor(cursor)

    # ---------------------------------
    # History
    # ---------------------------------

    def history_up(self):
        if not self.history:
            return

        self.history_index = max(
            0,
            self.history_index - 1
        )

        self.replace_current_line(
            self.history[
                self.history_index
            ]
        )

    def history_down(self):
        if not self.history:
            return

        self.history_index = min(
            len(self.history),
            self.history_index + 1
        )

        if self.history_index >= len(
            self.history
        ):
            self.replace_current_line("")
        else:
            self.replace_current_line(
                self.history[
                    self.history_index
                ]
            )

    # ---------------------------------
    # Replace current line
    # ---------------------------------

    def replace_current_line(self, text):
        cursor = self.textCursor()

        cursor.movePosition(
            QTextCursor.End
        )

        self.setTextCursor(cursor)

        cursor = self.textCursor()

        cursor.setPosition(
            self.prompt_position
        )

        cursor.movePosition(
            QTextCursor.End,
            QTextCursor.KeepAnchor,
        )

        cursor.removeSelectedText()

        cursor.insertText(
            text,
            self.normal_text_format(),
        )

        self.setTextCursor(cursor)
        self.reset_text_format()

    def insert_prompt(self):
        self.reset_text_format()

        cursor = self.textCursor()

        cursor.movePosition(
            QTextCursor.End
        )

        self.setTextCursor(cursor)

        # Add prompt on new line if needed
        text = self.toPlainText()

        if text and not text.endswith("\n"):
            self.insert_normal_text("\n")

        self.insert_normal_text(self.prompt)

        self.prompt_position = (
            self.textCursor().position()
        )

        self.reset_text_format()

    def insert_output_text(self, text, message_type=None):
        cursor = self.textCursor()
        cursor.movePosition(
            QTextCursor.End
        )

        self.setTextCursor(cursor)

        self.reset_text_format()

        text_format = self.output_text_format(
            text,
            message_type,
        )

        if text_format is None:
            text_format = self.normal_text_format()

        cursor.insertText(text, text_format)

        self.setTextCursor(cursor)
        self.reset_text_format()

    def insert_normal_text(self, text):
        cursor = self.textCursor()
        cursor.movePosition(
            QTextCursor.End
        )

        self.setTextCursor(cursor)

        cursor.insertText(
            text,
            self.normal_text_format(),
        )

        self.setTextCursor(cursor)
        self.reset_text_format()

    def normal_text_format(self):
        text_format = QTextCharFormat()
        text_format.setForeground(
            self.normal_text_color
        )

        return text_format

    def set_normal_text_color(self, color):
        self.normal_text_color = QColor(color)
        self.reset_text_format()

    def reset_text_format(self):
        text_format = self.normal_text_format()

        cursor = self.textCursor()
        cursor.setCharFormat(text_format)

        self.setTextCursor(cursor)
        self.setCurrentCharFormat(text_format)

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

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        cursor = self.textCursor()

        if (
            cursor.position()
            < self.prompt_position
        ):
            cursor.movePosition(
                QTextCursor.End
            )

            self.setTextCursor(cursor)
