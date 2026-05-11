class MathToolError(Exception):
    def __init__(
        self,
        category,
        message,
        line=None,
        column=None,
        token=None,
    ):
        self.category = category
        self.message = message
        self.line = line
        self.column = column
        self.token = token

    def __str__(self):
        parts = [f"{self.category}:"]

        parts.append(self.message)

        if self.line is not None:
            parts.append(
                f"Line {self.line}"
            )

        if self.column is not None:
            parts.append(
                f"Column {self.column}"
            )

        if self.token is not None:
            parts.append(
                f"Token: {self.token}"
            )

        return "\n".join(parts)


class LexerError(MathToolError):
    def __init__(
        self,
        message,
        line=None,
        column=None,
        token=None,
    ):
        super().__init__(
            "LexerError",
            message,
            line,
            column,
            token,
        )


class ParserError(MathToolError):
    def __init__(
        self,
        message,
        line=None,
        column=None,
        token=None,
    ):
        super().__init__(
            "ParserError",
            message,
            line,
            column,
            token,
        )


class SemanticError(MathToolError):
    def __init__(
        self,
        message,
        line=None,
        column=None,
        token=None,
    ):
        super().__init__(
            "SemanticError",
            message,
            line,
            column,
            token,
        )


class RuntimeError(MathToolError):
    def __init__(
        self,
        message,
        line=None,
        column=None,
        token=None,
    ):
        super().__init__(
            "RuntimeError",
            message,
            line,
            column,
            token,
        )