from PySide6.QtCore import Qt

from PySide6.QtGui import QAction, QKeySequence

from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.documentation.html import (
    function_help_to_html,
    help_home_to_html,
)
from gui.help_viewer import HelpViewer


class DocumentationPanel(QWidget):
    def __init__(self, help_database, parent=None):
        super().__init__(parent)

        self.help_database = help_database
        self.current_topic = None
        self.recent_topics = []

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(
            "Search documentation"
        )
        self.search_edit.setClearButtonEnabled(True)

        self.home_button = QPushButton("Home")
        self.home_button.setObjectName("secondaryButton")

        self.result_list = QListWidget()
        self.result_list.setUniformItemSizes(True)

        self.index_tree = QTreeWidget()
        self.index_tree.setHeaderHidden(True)

        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderHidden(True)

        self.examples_list = QListWidget()
        self.examples_list.setUniformItemSizes(True)

        self.navigation_tabs = QTabWidget()
        self.navigation_tabs.addTab(self.result_list, "Search")
        self.navigation_tabs.addTab(self.index_tree, "A-Z")
        self.navigation_tabs.addTab(self.category_tree, "Categories")
        self.navigation_tabs.addTab(self.examples_list, "Examples")

        self.signature_label = QLabel()
        self.signature_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )
        self.signature_label.setWordWrap(True)

        self.browser = HelpViewer()

        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        self.setLayout(layout)

        splitter = QSplitter(Qt.Horizontal)

        left = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
        left.setLayout(left_layout)

        left_layout.addWidget(self.search_edit)
        left_layout.addWidget(self.home_button)
        left_layout.addWidget(self.navigation_tabs)

        detail = QWidget()
        detail_layout = QVBoxLayout()
        detail_layout.setContentsMargins(0, 0, 0, 0)
        detail_layout.setSpacing(6)
        detail.setLayout(detail_layout)

        detail_layout.addWidget(self.signature_label)
        detail_layout.addWidget(self.browser)

        splitter.addWidget(left)
        splitter.addWidget(detail)
        splitter.setSizes([320, 760])

        layout.addWidget(splitter)

        self.search_edit.textChanged.connect(
            self.update_results
        )
        self.home_button.clicked.connect(self.show_home)
        self.result_list.currentItemChanged.connect(
            self.on_result_changed
        )
        self.index_tree.itemClicked.connect(
            self.on_tree_item_clicked
        )
        self.category_tree.itemClicked.connect(
            self.on_tree_item_clicked
        )
        self.examples_list.currentItemChanged.connect(
            self.on_example_changed
        )
        self.browser.anchorClicked.connect(
            self.on_anchor_clicked
        )

        self.install_shortcuts()
        self.refresh()

    def install_shortcuts(self):
        focus_search_action = QAction(self)
        focus_search_action.setShortcut(QKeySequence.Find)
        focus_search_action.setShortcutContext(
            Qt.WidgetWithChildrenShortcut
        )
        focus_search_action.triggered.connect(
            self.focus_search
        )
        self.addAction(focus_search_action)

        quick_search_action = QAction(self)
        quick_search_action.setShortcut(QKeySequence("Ctrl+K"))
        quick_search_action.setShortcutContext(
            Qt.WidgetWithChildrenShortcut
        )
        quick_search_action.triggered.connect(
            self.focus_search
        )
        self.addAction(quick_search_action)

    def refresh(self):
        self.help_database.refresh()
        self.populate_navigation()
        self.update_results(self.search_edit.text())

        if self.current_topic:
            self.show_topic(self.current_topic)
        elif not self.search_edit.text().strip():
            self.show_home()

    def populate_navigation(self):
        self.populate_index()
        self.populate_categories()
        self.populate_examples()

    def populate_index(self):
        self.index_tree.blockSignals(True)
        self.index_tree.clear()

        for letter, entries in (
            self.help_database.entries_by_letter().items()
        ):
            letter_item = QTreeWidgetItem([letter])
            letter_item.setExpanded(letter in {"A", "B", "C"})
            self.index_tree.addTopLevelItem(letter_item)

            for entry in entries:
                letter_item.addChild(
                    self.topic_tree_item(entry)
                )

        self.index_tree.blockSignals(False)

    def populate_categories(self):
        self.category_tree.blockSignals(True)
        self.category_tree.clear()

        for category, entries in (
            self.help_database.entries_by_category().items()
        ):
            category_item = QTreeWidgetItem([category])
            category_item.setData(
                0,
                Qt.UserRole,
                f"category:{category}",
            )
            category_item.setExpanded(
                category in {
                    "Plotting",
                    "Array Construction And Shape",
                    "Builtin Functions",
                    "Language Basics",
                }
            )
            self.category_tree.addTopLevelItem(category_item)

            for entry in entries:
                category_item.addChild(
                    self.topic_tree_item(entry)
                )

        self.category_tree.blockSignals(False)

    def populate_examples(self):
        self.examples_list.blockSignals(True)
        self.examples_list.clear()

        for entry in self.help_database.all_entries():
            if not entry.examples:
                continue

            item = QListWidgetItem(
                f"{entry.display_name} - {entry.category}"
            )
            item.setData(Qt.UserRole, entry.functionName)
            item.setToolTip(entry.h1Line)
            self.examples_list.addItem(item)

        self.examples_list.blockSignals(False)

    def topic_tree_item(self, entry):
        item = QTreeWidgetItem(
            [
                entry.display_name,
            ]
        )
        item.setData(0, Qt.UserRole, entry.functionName)
        item.setToolTip(0, entry.h1Line)

        return item

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
                f"{entry.display_name}{description}"
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
            if query.strip():
                self.navigation_tabs.setCurrentWidget(
                    self.result_list
                )
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

        if not query.strip() and self.current_topic is None:
            self.show_home()

    def on_result_changed(self, current, previous):
        if current is None:
            return

        self.show_topic(
            current.data(Qt.UserRole)
        )

    def on_tree_item_clicked(self, item, column):
        value = item.data(0, Qt.UserRole)

        if not value:
            item.setExpanded(not item.isExpanded())
            return

        if str(value).startswith("category:"):
            self.open_category(
                str(value).removeprefix("category:")
            )
            return

        self.open_topic(value)

    def on_example_changed(self, current, previous):
        if current is None:
            return

        self.open_topic(
            current.data(Qt.UserRole)
        )

    def show_home(self):
        self.current_topic = None
        self.signature_label.setText("MathTool Help")
        self.browser.setHtml(
            help_home_to_html(
                self.help_database,
                self.recent_topic_entries(),
            )
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
        self.signature_label.setText(
            entry.signature
            or f"{entry.display_name} - {entry.category}"
        )
        self.signature_label.setToolTip(entry.h1Line)
        self.browser.setHtml(
            function_help_to_html(entry)
        )
        self.remember_topic(entry.functionName)

    def remember_topic(self, topic):
        key = str(topic).lower()
        self.recent_topics = [
            item
            for item in self.recent_topics
            if item.lower() != key
        ]
        self.recent_topics.insert(0, topic)
        self.recent_topics = self.recent_topics[:8]

    def recent_topic_entries(self):
        entries = []

        for topic in self.recent_topics:
            entry = self.help_database.get(topic)

            if entry is not None:
                entries.append(entry)

        return entries

    def on_anchor_clicked(self, url):
        target = url.toString()

        if target.startswith("seealso:"):
            self.open_topic(target.removeprefix("seealso:"))
            return

        if target.startswith("topic:"):
            self.open_topic(target.removeprefix("topic:"))
            return

        if target.startswith("category:"):
            self.open_category(target.removeprefix("category:"))
            return

        if target.startswith("#"):
            self.browser.scrollToAnchor(target[1:])

    def open_topic(self, topic):
        entry = self.help_database.get(topic)

        if entry is None:
            self.search_edit.setText(str(topic))
            self.current_topic = None
            self.signature_label.setText("")
            self.browser.setPlainText(
                f"No help available for {topic}"
            )
            return

        if self.search_edit.text() != entry.display_name:
            self.search_edit.blockSignals(True)
            self.search_edit.setText(entry.display_name)
            self.search_edit.blockSignals(False)
            self.update_results(self.search_edit.text())

        self.show_topic(entry.functionName)
        self.select_result(entry.functionName)

    def open_category(self, category):
        self.navigation_tabs.setCurrentWidget(
            self.result_list
        )
        self.search_edit.setText(category)
        self.focus_search(select_all=False)

    def select_result(self, topic):
        for row in range(self.result_list.count()):
            item = self.result_list.item(row)

            if (
                item.data(Qt.UserRole).lower()
                == str(topic).lower()
            ):
                self.result_list.setCurrentRow(row)
                break

    def focus_search(self, select_all=True):
        self.search_edit.setFocus()

        if select_all:
            self.search_edit.selectAll()
