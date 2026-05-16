from PySide6.QtWidgets import (
    QPlainTextEdit,
    QTextEdit,
    QWidget,
)

from PySide6.QtGui import (
    QColor,
    QTextFormat,
    QTextCursor,
    QPainter,
    QPen,
    QBrush,
    QPolygon,
)

from PySide6.QtCore import (
    QPoint,
    QRect,
    QSize,
    Qt,
    Signal,
)


DEFAULT_EDITOR_THEME = {
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
}


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)

        self.editor = editor

        self.setCursor(Qt.PointingHandCursor)

    def sizeHint(self):
        return QSize(
            self.editor.line_number_area_width(),
            0,
        )

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(
            event
        )

    def mousePressEvent(self, event):
        self.editor.line_number_area_mouse_press_event(
            event
        )


class CodeEditor(QPlainTextEdit):
    breakpoint_toggled = Signal(int, bool)

    def __init__(self):
        super().__init__()

        self.breakpoints = set()

        self.debug_line = None

        self.theme = DEFAULT_EDITOR_THEME.copy()

        self.highlight_current_line_enabled = True

        self.auto_indent_enabled = True

        self.show_line_numbers = True

        self.marker_margin_width = 30

        self.line_number_area = LineNumberArea(
            self
        )

        self.blockCountChanged.connect(
            self.update_line_number_area_width
        )

        self.updateRequest.connect(
            self.update_line_number_area
        )

        self.cursorPositionChanged.connect(
            self.highlight_current_line
        )

        self.update_line_number_area_width(0)

        self.highlight_current_line()

    def setFont(self, font):
        super().setFont(font)

        if hasattr(self, "line_number_area"):
            self.update_line_number_area_width(0)

            self.line_number_area.update()

    def line_number_area_width(self):
        digits = len(
            str(
                max(1, self.blockCount())
            )
        )

        digit_width = 0

        if self.show_line_numbers:
            digit_width = (
                self.fontMetrics()
                .horizontalAdvance("9")
                * digits
            )

        return (
            self.marker_margin_width
            + digit_width
            + 12
        )

    def apply_editor_preferences(
        self,
        preferences,
        theme,
    ):
        self.theme = {
            **DEFAULT_EDITOR_THEME,
            **theme,
        }

        font = self.font()

        font.setFamily(
            preferences.get(
                "editor_font_family",
                font.family(),
            )
        )

        font.setPointSize(
            int(
                preferences.get(
                    "editor_font_size",
                    font.pointSize(),
                )
            )
        )

        self.setFont(font)

        self.setLineWrapMode(
            QPlainTextEdit.WidgetWidth
            if preferences.get("word_wrap", False)
            else QPlainTextEdit.NoWrap
        )

        self.setTabStopDistance(
            self.fontMetrics().horizontalAdvance(" ")
            * int(preferences.get("tab_width", 4))
        )

        self.auto_indent_enabled = bool(
            preferences.get("auto_indent", True)
        )

        self.highlight_current_line_enabled = bool(
            preferences.get("highlight_current_line", True)
        )

        self.show_line_numbers = bool(
            preferences.get("show_line_numbers", True)
        )

        self.setStyleSheet(
            f"""
            QPlainTextEdit {{
                background-color: {self.theme["editor_background"]};
                color: {self.theme["editor_foreground"]};
                border: 1px solid {self.theme["editor_border"]};
                border-radius: 3px;
                font-family: '{font.family()}';
                font-size: {font.pointSize()}pt;
            }}
            """
        )

        self.update_line_number_area_width(0)

        self.highlight_current_line()

        self.line_number_area.update()

    def update_line_number_area_width(self, _):
        self.setViewportMargins(
            self.line_number_area_width(),
            0,
            0,
            0,
        )

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(
                0,
                dy,
            )

        else:
            self.line_number_area.update(
                0,
                rect.y(),
                self.line_number_area.width(),
                rect.height(),
            )

        if rect.contains(
            self.viewport().rect()
        ):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        contents = self.contentsRect()

        self.line_number_area.setGeometry(
            QRect(
                contents.left(),
                contents.top(),
                self.line_number_area_width(),
                contents.height(),
            )
        )

    def line_number_area_paint_event(self, event):
        painter = QPainter(
            self.line_number_area
        )

        painter.fillRect(
            event.rect(),
            QColor(self.theme["gutter_background"]),
        )

        block = self.firstVisibleBlock()

        block_number = block.blockNumber()

        top = int(
            self.blockBoundingGeometry(block)
            .translated(self.contentOffset())
            .top()
        )

        line_number_width = (
            self.line_number_area.width()
            - self.marker_margin_width
            - 6
        )

        while (
            block.isValid()
            and top <= event.rect().bottom()
        ):
            height = int(
                self.blockBoundingRect(block)
                .height()
            )

            bottom = top + height

            if (
                block.isVisible()
                and bottom >= event.rect().top()
            ):
                line_number = block_number + 1

                if self.debug_line == line_number:
                    painter.fillRect(
                        0,
                        top,
                        self.line_number_area.width(),
                        height,
                        QColor(
                            self.theme[
                                "debug_line_background"
                            ]
                        ),
                    )

                elif (
                    self.highlight_current_line_enabled
                    and
                    self.textCursor().blockNumber()
                    == block_number
                ):
                    painter.fillRect(
                        0,
                        top,
                        self.line_number_area.width(),
                        height,
                        QColor(
                            self.theme[
                                "current_line_background"
                            ]
                        ),
                    )

                self._paint_breakpoint(
                    painter,
                    line_number,
                    top,
                    height,
                )

                self._paint_debug_arrow(
                    painter,
                    line_number,
                    top,
                    height,
                )

                if self.show_line_numbers:
                    if (
                        (
                            self.highlight_current_line_enabled
                            and self.textCursor().blockNumber()
                            == block_number
                        )
                        or self.debug_line == line_number
                    ):
                        painter.setPen(
                            QColor(
                                self.theme[
                                    "current_line_number"
                                ]
                            )
                        )

                    else:
                        painter.setPen(
                            QColor(
                                self.theme["line_number"]
                            )
                        )

                    painter.drawText(
                        self.marker_margin_width,
                        top,
                        line_number_width,
                        self.fontMetrics().height(),
                        Qt.AlignRight,
                        str(line_number),
                    )

            block = block.next()

            top = bottom

            block_number += 1

    def _paint_breakpoint(
        self,
        painter,
        line_number,
        top,
        height,
    ):
        if line_number not in self.breakpoints:
            return

        radius = 5

        center = QPoint(
            10,
            top + height // 2,
        )

        painter.setPen(
            QPen(
                QColor(
                    self.theme["breakpoint_border"]
                ),
                1,
            )
        )

        painter.setBrush(
            QBrush(
                QColor(self.theme["breakpoint"])
            )
        )

        painter.drawEllipse(
            center,
            radius,
            radius,
        )

    def _paint_debug_arrow(
        self,
        painter,
        line_number,
        top,
        height,
    ):
        if self.debug_line != line_number:
            return

        middle = top + height // 2

        arrow = QPolygon(
            [
                QPoint(18, middle - 6),
                QPoint(27, middle),
                QPoint(18, middle + 6),
            ]
        )

        painter.setPen(Qt.NoPen)

        painter.setBrush(
            QBrush(
                QColor(self.theme["execution_arrow"])
            )
        )

        painter.drawPolygon(arrow)

    def line_number_area_mouse_press_event(
        self,
        event,
    ):
        if event.button() != Qt.LeftButton:
            return

        position = (
            event.position().toPoint()
            if hasattr(event, "position")
            else event.pos()
        )

        line = self.line_at_y(position.y())

        if line is not None:
            self.toggle_breakpoint(line)

    def line_at_y(self, y):
        block = self.firstVisibleBlock()

        block_number = block.blockNumber()

        top = int(
            self.blockBoundingGeometry(block)
            .translated(self.contentOffset())
            .top()
        )

        while block.isValid():
            height = int(
                self.blockBoundingRect(block)
                .height()
            )

            bottom = top + height

            if (
                block.isVisible()
                and top <= y <= bottom
            ):
                return block_number + 1

            if top > y:
                break

            block = block.next()

            top = bottom

            block_number += 1

        return None

    def toggle_breakpoint(self, line):
        enabled = line not in self.breakpoints

        self.set_breakpoint(
            line,
            enabled,
        )

    def set_breakpoint(
        self,
        line,
        enabled=True,
        emit_signal=True,
    ):
        if line is None:
            return

        line = int(line)

        if line < 1:
            return

        changed = False

        if enabled:
            if line not in self.breakpoints:
                self.breakpoints.add(line)

                changed = True

        else:
            if line in self.breakpoints:
                self.breakpoints.remove(line)

                changed = True

        if not changed:
            return

        self.line_number_area.update()

        if emit_signal:
            self.breakpoint_toggled.emit(
                line,
                enabled,
            )

    def set_breakpoints(self, lines):
        self.breakpoints = {
            int(line)
            for line in lines
            if int(line) > 0
        }

        self.line_number_area.update()

    def highlight_debug_line(self, line):
        self.debug_line = (
            int(line)
            if line is not None
            else None
        )

        self.highlight_current_line()

        self.line_number_area.update()

    def highlight_current_line(self):
        extra_selections = []

        if (
            self.highlight_current_line_enabled
            and not self.isReadOnly()
        ):
            selection = (
                QTextEdit.ExtraSelection()
            )

            line_color = QColor(
                self.theme["current_line_background"]
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

        if self.debug_line is not None:
            block = (
                self.document()
                .findBlockByLineNumber(
                    self.debug_line - 1
                )
            )

            if block.isValid():
                selection = (
                    QTextEdit.ExtraSelection()
                )

                selection.format.setBackground(
                    QColor(
                        self.theme[
                            "debug_line_background"
                        ]
                    )
                )

                selection.format.setProperty(
                    QTextFormat.FullWidthSelection,
                    True,
                )

                selection.cursor = QTextCursor(block)

                selection.cursor.clearSelection()

                extra_selections.append(
                    selection
                )

        self.setExtraSelections(
            extra_selections
        )

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

        if not self.auto_indent_enabled:
            return

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
