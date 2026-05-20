import os

os.environ.setdefault(
    "QT_QPA_PLATFORM",
    "offscreen",
)

import pytest
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication

from gui.command_window import CommandWindow


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def char_color(widget, text, *, last=False):
    plain_text = widget.toPlainText()

    if last:
        start = plain_text.rfind(text)
    else:
        start = plain_text.index(text)

    cursor = QTextCursor(widget.document())
    cursor.setPosition(start)
    cursor.movePosition(
        QTextCursor.Right,
        QTextCursor.KeepAnchor,
        len(text),
    )

    return cursor.charFormat().foreground().color().name()


def test_command_window_resets_text_color_after_error(app):
    def fail(command):
        raise Exception("boom")

    command_window = CommandWindow(fail)

    command_window.insertPlainText("bad")
    command_window.execute_current_line()
    command_window.insertPlainText("next")

    assert char_color(command_window, "boom") == "#ff4d4d"
    assert char_color(
        command_window,
        ">> ",
        last=True,
    ) == "#d4d4d4"
    assert char_color(command_window, "next") == "#d4d4d4"
