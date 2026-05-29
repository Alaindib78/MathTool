import numpy as np

from core.control import is_lti_model
from core.runtime.formatting import format_value
from core.runtime.symbolic import SymbolicValue

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
)

from PySide6.QtCore import Qt


class VariableEditor(QWidget):
    def __init__(
        self,
        variable_name,
        value,
        update_callback=None,
        display_format=None,
    ):
        super().__init__()

        self.variable_name = variable_name

        self.value = value

        self.update_callback = (
            update_callback
        )

        self.display_format = display_format

        layout = QVBoxLayout()

        self.setLayout(layout)

        self.table = QTableWidget()

        layout.addWidget(self.table)

        self.populate_table()

        self.table.itemChanged.connect(
            self.handle_item_changed
        )

    # ---------------------------------
    # Populate Table
    # ---------------------------------

    def populate_table(self):
        self.table.blockSignals(True)
        value = self.value

        if isinstance(value, str):
            self.table.setRowCount(1)
            self.table.setColumnCount(1)

            item = QTableWidgetItem(value)

            self.table.setItem(0, 0, item)

            self.table.blockSignals(False)

            return

        if isinstance(value, SymbolicValue):
            self.table.setRowCount(1)
            self.table.setColumnCount(1)

            item = QTableWidgetItem(str(value))

            self.table.setItem(0, 0, item)

            self.table.blockSignals(False)

            return

        if isinstance(value, dict):
            self.table.setRowCount(len(value))
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(
                ["Field", "Value"]
            )

            for row, (key, field_value) in enumerate(
                value.items()
            ):
                self.table.setItem(
                    row,
                    0,
                    QTableWidgetItem(str(key)),
                )
                self.table.setItem(
                    row,
                    1,
                    QTableWidgetItem(
                        self.format_display_value(
                            field_value
                        )
                    ),
                )

            self.table.resizeColumnsToContents()

            self.table.blockSignals(False)

            return

        if is_lti_model(value):
            properties = value.properties()
            self.table.setRowCount(len(properties))
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(
                ["Property", "Value"]
            )

            for row, (key, property_value) in enumerate(
                properties.items()
            ):
                name_item = QTableWidgetItem(str(key))
                value_item = QTableWidgetItem(
                    self.format_display_value(
                        property_value
                    )
                )
                name_item.setFlags(
                    name_item.flags() & ~Qt.ItemIsEditable
                )
                value_item.setFlags(
                    value_item.flags() & ~Qt.ItemIsEditable
                )
                self.table.setItem(row, 0, name_item)
                self.table.setItem(row, 1, value_item)

            self.table.resizeColumnsToContents()
            self.table.blockSignals(False)
            return

        # Scalar
        if np.isscalar(value):
            self.table.setRowCount(1)
            self.table.setColumnCount(1)

            self.table.setItem(
                0,
                0,
                QTableWidgetItem(
                    self.format_display_value(value)
                ),
            )

            self.table.blockSignals(False)

            return

        # Convert lists to arrays
        value = np.array(value)

        if value.ndim == 1:
            value = value.reshape(1, -1)

        rows, cols = value.shape

        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)

        MAX_DISPLAY_SIZE = 200

        if value.size > MAX_DISPLAY_SIZE:
            value = value.flatten()[
                :MAX_DISPLAY_SIZE
            ].reshape(-1, 1)

        for r in range(rows):
            for c in range(cols):
                item = QTableWidgetItem(
                    self.format_display_value(
                        value[r, c]
                    )
                )

                self.table.setItem(
                    r,
                    c,
                    item,
                )

        self.table.setHorizontalHeaderLabels(
            [
                str(i + 1)
                for i in range(cols)
            ]
        )

        self.table.setVerticalHeaderLabels(
            [
                str(i + 1)
                for i in range(rows)
            ]
        )

        self.table.resizeColumnsToContents()
        self.table.blockSignals(False)

    def format_display_value(self, value):
        return format_value(
            value,
            self.display_format,
        )

    def refresh_display_format(self, display_format):
        self.display_format = display_format
        self.populate_table()

    # ---------------------------------
    # Handle Editing
    # ---------------------------------

    def handle_item_changed(self, item):
        try:
            row = item.row()
            col = item.column()

            text = item.text()

            # Try numeric conversion
            try:
                value = complex(
                    text.replace("i", "j")
                    .replace(" ", "")
                )

                if value.imag == 0:
                    value = value.real
            except Exception:
                try:
                    value = float(text)
                except Exception:
                    value = text

            # Scalar
            if np.isscalar(self.value):
                self.value = value

            else:
                arr = np.array(self.value)

                if arr.ndim == 1:
                    arr[col] = value
                else:
                    arr[row, col] = value

                self.value = arr

            if self.update_callback:
                self.update_callback(
                    self.variable_name,
                    self.value,
                )

        except Exception as e:
            print(e)
