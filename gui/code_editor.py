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
            QColor("#252526"),
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
                        QColor("#3A3320"),
                    )

                elif (
                    self.textCursor().blockNumber()
                    == block_number
                ):
                    painter.fillRect(
                        0,
                        top,
                        self.line_number_area.width(),
                        height,
                        QColor("#2A2D2E"),
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

                if (
                    self.textCursor().blockNumber()
                    == block_number
                    or self.debug_line == line_number
                ):
                    painter.setPen(
                        QColor("#CCCCCC")
                    )

                else:
                    painter.setPen(
                        QColor("#858585")
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
                QColor("#F14C4C"),
                1,
            )
        )

        painter.setBrush(
            QBrush(QColor("#E51400"))
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
            QBrush(QColor("#DCDCAA"))
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
                    QColor("#3A3320")
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
