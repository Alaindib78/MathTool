import numpy as np

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
    ):
        super().__init__()

        self.variable_name = variable_name

        self.value = value

        self.update_callback = (
            update_callback
        )

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

            return

        if isinstance(value, SymbolicValue):
            self.table.setRowCount(1)
            self.table.setColumnCount(1)

            item = QTableWidgetItem(str(value))

            self.table.setItem(0, 0, item)

            return

        # Scalar
        if np.isscalar(value):
            self.table.setRowCount(1)
            self.table.setColumnCount(1)

            self.table.setItem(
                0,
                0,
                QTableWidgetItem(str(value)),
            )

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
                    str(value[r, c])
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
