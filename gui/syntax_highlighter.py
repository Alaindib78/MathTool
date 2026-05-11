from PySide6.QtGui import (
    QColor,
    QTextCharFormat,
    QFont,
    QSyntaxHighlighter,
)

from PySide6.QtCore import QRegularExpression


class MathToolSyntaxHighlighter(
    QSyntaxHighlighter
):
    def __init__(self, document):
        super().__init__(document)

        self.rules = []

        # ---------------------------------
        # Keywords
        # ---------------------------------

        keyword_format = QTextCharFormat()

        keyword_format.setForeground(
            QColor("#569CD6")
        )

        keyword_format.setFontWeight(
            QFont.Bold
        )

        keywords = [
            "if",
            "elseif",
            "else",
            "end",
            "while",
            "for",
            "function",
            "return",
            "true",
            "false",
        ]

        for word in keywords:
            pattern = (
                QRegularExpression(
                    rf"\b{word}\b"
                )
            )

            self.rules.append(
                (pattern, keyword_format)
            )

        # ---------------------------------
        # Numbers
        # ---------------------------------

        number_format = QTextCharFormat()

        number_format.setForeground(
            QColor("#B5CEA8")
        )

        self.rules.append(
            (
                QRegularExpression(
                    r"\b\d+(\.\d+)?\b"
                ),
                number_format,
            )
        )

        # ---------------------------------
        # Strings
        # ---------------------------------

        string_format = QTextCharFormat()

        string_format.setForeground(
            QColor("#CE9178")
        )

        self.rules.append(
            (
                QRegularExpression(
                    r'"[^"]*"'
                ),
                string_format,
            )
        )

        # ---------------------------------
        # Comments
        # ---------------------------------

        comment_format = QTextCharFormat()

        comment_format.setForeground(
            QColor("#6A9955")
        )

        self.rules.append(
            (
                QRegularExpression(
                    r"%[^\n]*"
                ),
                comment_format,
            )
        )

        # ---------------------------------
        # Functions
        # ---------------------------------

        function_format = QTextCharFormat()

        function_format.setForeground(
            QColor("#DCDCAA")
        )

        self.rules.append(
            (
                QRegularExpression(
                    r"\b[A-Za-z_][A-Za-z0-9_]*(?=\()"
                ),
                function_format,
            )
        )

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            iterator = pattern.globalMatch(text)

            while iterator.hasNext():
                match = iterator.next()

                self.setFormat(
                    match.capturedStart(),
                    match.capturedLength(),
                    fmt,
                )