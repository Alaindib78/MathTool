from email.mime import text

from PySide6.QtWidgets import (
    QPlainTextEdit,
)

from PySide6.QtGui import (
    QTextCursor,
    QFont,
)

from PySide6.QtCore import Qt


class CommandWindow(QPlainTextEdit):
    def __init__(self, execute_callback):
        super().__init__()

        self.execute_callback = (
            execute_callback
        )

        self.history = []

        self.history_index = -1

        self.prompt = ">> "

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

        self.insert_prompt()

        self.setUndoRedoEnabled(False)

        self.prompt_position = 0

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
        self.insertPlainText("\n")

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
                    self.insertPlainText(
                        str(result)
                    )

                    self.insertPlainText(
                        "\n"
                    )

            except Exception as e:
                self.insertPlainText(
                    str(e)
                )

                self.insertPlainText(
                    "\n"
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

        cursor.insertText(text)

        self.setTextCursor(cursor)

    def insert_prompt(self):
        cursor = self.textCursor()

        cursor.movePosition(
            QTextCursor.End
        )

        self.setTextCursor(cursor)

        # Add prompt on new line if needed
        text = self.toPlainText()

        if text and not text.endswith("\n"):
            self.insertPlainText("\n")

        self.insertPlainText(self.prompt)

        self.prompt_position = (
            self.textCursor().position()
        )

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