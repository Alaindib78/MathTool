from core.lexer.token import TokenType, Token


KEYWORDS = {
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "elseif": TokenType.ELSEIF,
    "end": TokenType.END,
    "for": TokenType.FOR,
    "while": TokenType.WHILE,
    "function": TokenType.FUNCTION,
    "return": TokenType.RETURN,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
}


class Lexer:
    def __init__(self, source):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1

    def tokenize(self):
        tokens = []

        while not self.is_at_end():
            char = self.peek()

            # Ignore whitespace
            if char in " \t\r":
                self.advance()
                continue

            # Newlines
            if char == "\n":
                self.advance_line()
                continue

            # Numbers
            if char.isdigit():
                tokens.append(self.number())
                continue

            # Identifiers / keywords
            if char.isalpha() or char == "_":
                tokens.append(self.identifier())
                continue

            # Single-character tokens
            single_char_tokens = {
                "+": TokenType.PLUS,
                "-": TokenType.MINUS,
                "*": TokenType.STAR,
                "/": TokenType.SLASH,
                "^": TokenType.CARET,
                "%": TokenType.MODULO,
                "=": TokenType.EQUAL,
                "(": TokenType.LPAREN,
                ")": TokenType.RPAREN,
                "[": TokenType.LBRACKET,
                "]": TokenType.RBRACKET,
                ",": TokenType.COMMA,
                ";": TokenType.SEMICOLON,
            }

            if char in single_char_tokens:
                token = Token(
                    single_char_tokens[char],
                    char,
                    self.line,
                    self.column
                )

                tokens.append(token)
                self.advance()
                continue

            raise Exception(
                f"Unexpected character '{char}' "
                f"at line {self.line}, column {self.column}"
            )

        tokens.append(
            Token(TokenType.EOF, None, self.line, self.column)
        )

        return tokens

    def number(self):
        start_column = self.column
        number_str = ""

        while not self.is_at_end() and (
            self.peek().isdigit() or self.peek() == "."
        ):
            number_str += self.advance()

        return Token(
            TokenType.NUMBER,
            float(number_str),
            self.line,
            start_column
        )

    def identifier(self):
        start_column = self.column
        identifier = ""

        while not self.is_at_end() and (
            self.peek().isalnum() or self.peek() == "_"
        ):
            identifier += self.advance()

        token_type = KEYWORDS.get(
            identifier,
            TokenType.IDENTIFIER
        )

        return Token(
            token_type,
            identifier,
            self.line,
            start_column
        )

    def peek(self):
        return self.source[self.position]

    def advance(self):
        char = self.source[self.position]
        self.position += 1
        self.column += 1
        return char

    def advance_line(self):
        self.position += 1
        self.line += 1
        self.column = 1

    def is_at_end(self):
        return self.position >= len(self.source)