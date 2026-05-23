from PySide6.QtWidgets import QTextBrowser


class HelpViewer(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setOpenLinks(False)
        self.setStyleSheet(
            """
            QTextBrowser {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                padding: 8px;
            }
            """
        )
