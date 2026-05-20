from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from core.documentation.html import function_help_to_html


class DocumentationPanel(QWidget):
    def __init__(self, help_database, parent=None):
        super().__init__(parent)

        self.help_database = help_database
        self.current_topic = None

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(
            "Search documentation"
        )

        self.result_list = QListWidget()

        self.signature_label = QLabel()
        self.signature_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        self.browser = QTextBrowser()
        self.browser.setOpenLinks(False)

        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        self.setLayout(layout)

        layout.addWidget(self.search_edit)

        splitter = QSplitter(Qt.Vertical)

        splitter.addWidget(self.result_list)

        detail = QWidget()
        detail_layout = QVBoxLayout()
        detail_layout.setContentsMargins(0, 0, 0, 0)
        detail_layout.setSpacing(6)
        detail.setLayout(detail_layout)

        detail_layout.addWidget(self.signature_label)
        detail_layout.addWidget(self.browser)

        splitter.addWidget(detail)
        splitter.setSizes([180, 420])

        layout.addWidget(splitter)

        self.search_edit.textChanged.connect(
            self.update_results
        )
        self.result_list.currentItemChanged.connect(
            self.on_result_changed
        )
        self.browser.anchorClicked.connect(
            self.on_anchor_clicked
        )

        self.refresh()

    def refresh(self):
        self.help_database.refresh()
        self.update_results(self.search_edit.text())

        if self.current_topic:
            self.show_topic(self.current_topic)

    def update_results(self, query):
        selected_topic = self.current_topic
        results = self.help_database.search(query)

        self.result_list.blockSignals(True)
        self.result_list.clear()

        selected_row = 0

        for index, entry in enumerate(results):
            description = (
                f" - {entry.h1Line}"
                if entry.h1Line
                else ""
            )
            item = QListWidgetItem(
                f"{entry.functionName}{description}"
            )
            item.setData(
                Qt.UserRole,
                entry.functionName,
            )
            item.setToolTip(entry.h1Line)
            self.result_list.addItem(item)

            if (
                selected_topic
                and entry.functionName.lower()
                == selected_topic.lower()
            ):
                selected_row = index

        self.result_list.blockSignals(False)

        if self.result_list.count():
            self.result_list.setCurrentRow(selected_row)
            self.show_topic(
                self.result_list.currentItem().data(
                    Qt.UserRole
                )
            )
        else:
            self.current_topic = None
            self.signature_label.setText("")
            self.browser.setPlainText("No documentation matches.")

    def on_result_changed(self, current, previous):
        if current is None:
            return

        self.show_topic(
            current.data(Qt.UserRole)
        )

    def show_topic(self, topic):
        entry = self.help_database.get(topic)

        if entry is None:
            self.current_topic = None
            self.signature_label.setText("")
            self.browser.setPlainText(
                f"No help available for {topic}"
            )
            return

        self.current_topic = entry.functionName
        self.signature_label.setText(entry.signature)
        self.signature_label.setToolTip(entry.h1Line)
        self.browser.setHtml(
            function_help_to_html(entry)
        )

    def on_anchor_clicked(self, url):
        target = url.toString()

        if target.startswith("seealso:"):
            self.open_topic(target.removeprefix("seealso:"))

    def open_topic(self, topic):
        self.search_edit.setText(topic)
        self.show_topic(topic)

        for row in range(self.result_list.count()):
            item = self.result_list.item(row)

            if (
                item.data(Qt.UserRole).lower()
                == topic.lower()
            ):
                self.result_list.setCurrentRow(row)
                break
