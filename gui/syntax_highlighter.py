from PySide6.QtGui import (
    QColor,
    QTextCharFormat,
    QFont,
    QSyntaxHighlighter,
)

from PySide6.QtCore import QRegularExpression


SYNTAX_THEMES = {
    "Dark": {
        "keyword": "#569CD6",
        "number": "#B5CEA8",
        "string": "#CE9178",
        "comment": "#6A9955",
        "function": "#DCDCAA",
    },
    "Light": {
        "keyword": "#0000FF",
        "number": "#098658",
        "string": "#A31515",
        "comment": "#008000",
        "function": "#795E26",
    },
    "High Contrast": {
        "keyword": "#00BFFF",
        "number": "#7FFF00",
        "string": "#FFB86C",
        "comment": "#A6E22E",
        "function": "#FFFF00",
    },
}


class MathToolSyntaxHighlighter(
    QSyntaxHighlighter
):
    def __init__(self, document, theme_name="Dark"):
        super().__init__(document)

        self.theme_name = theme_name

        self.rules = []

        self.set_theme(theme_name)

    def set_theme(self, theme_name):
        self.theme_name = theme_name

        colors = SYNTAX_THEMES.get(
            theme_name,
            SYNTAX_THEMES["Dark"],
        )

        self.rules = []

        # ---------------------------------
        # Keywords
        # ---------------------------------

        keyword_format = QTextCharFormat()

        keyword_format.setForeground(
            QColor(colors["keyword"])
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
            QColor(colors["number"])
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
            QColor(colors["string"])
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
            QColor(colors["comment"])
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
            QColor(colors["function"])
        )

        self.rules.append(
            (
                QRegularExpression(
                    r"\b[A-Za-z_][A-Za-z0-9_]*(?=\()"
                ),
                function_format,
            )
        )

        self.rehighlight()

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
