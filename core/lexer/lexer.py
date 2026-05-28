from core.lexer.token import TokenType, Token
from core.errors.errors import LexerError
from core.lexer.numeric_literals import parse_numeric_literal

KEYWORDS = {
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "elseif": TokenType.ELSEIF,
    "end": TokenType.END,
    "for": TokenType.FOR,
    "while": TokenType.WHILE,
    "function": TokenType.FUNCTION,
    "return": TokenType.RETURN,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
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

            # Strings
            if char == '"':
                tokens.append(self.string())
                continue

            if (
                char == "'"
                and self.is_single_quoted_string_start(tokens)
            ):
                tokens.append(
                    self.single_quoted_string()
                )
                continue

            # Numbers
            if char.isdigit():
                tokens.append(self.number())
                continue

            # Identifiers / keywords
            if char.isalpha() or char == "_":
                tokens.append(self.identifier())
                continue

            # ---------------------------------
            # MATLAB-style comments
            # ---------------------------------

            if char == "%":
                self.skip_comment()
                continue

            # Multi-character operators
            if char == "=" and self.peek_next() == "=":
                tokens.append(
                    Token(
                        TokenType.EQEQ,
                        "==",
                        self.line,
                        self.column
                    )
                )

                self.advance()
                self.advance()
                continue

            if char == "~" and self.peek_next() == "=":
                tokens.append(
                    Token(
                        TokenType.NEQ,
                        "~=",
                        self.line,
                        self.column
                    )
                )


                self.advance()
                self.advance()
                continue

            if char == "<" and self.peek_next() == "=":
                tokens.append(
                    Token(
                        TokenType.LTE,
                        "<=",
                        self.line,
                        self.column
                    )
                )

                self.advance()
                self.advance()
                continue    

            if char == ">" and self.peek_next() == "=":
                tokens.append(
                    Token(
                        TokenType.GTE,
                        ">=",
                        self.line,
                        self.column
                    )
                )

                self.advance()
                self.advance()
                continue    

            if char == "&" and self.peek_next() == "&":
                tokens.append(
                    Token(
                        TokenType.AND,
                        "&&",
                        self.line,
                        self.column
                    )
                )

                self.advance()
                self.advance()
                continue

            if char == "&":
                tokens.append(
                    Token(
                        TokenType.AND,
                        "&",
                        self.line,
                        self.column
                    )
                )

                self.advance()
                continue


            if char == "|" and self.peek_next() == "|":
                tokens.append(
                    Token(
                        TokenType.OR,
                        "||",
                        self.line,
                        self.column
                    )
                )   

                self.advance()
                self.advance()
                continue

            if char == "|":
                tokens.append(
                    Token(
                        TokenType.OR,
                        "|",
                        self.line,
                        self.column
                    )
                )

                self.advance()
                continue

            if char == "." and self.peek_next() == "*":
                tokens.append(
                    Token(
                        TokenType.DOTSTAR,
                        ".*",
                        self.line,
                        self.column
                    )
                )

                self.advance()
                self.advance()
                continue
    

            if char == "." and self.peek_next() == "/":
                tokens.append(
                    Token(
                        TokenType.DOTSLASH,
                        "./",
                        self.line,
                        self.column
                    )
                )

                self.advance()
                self.advance()
                continue

            if char == "." and self.peek_next() == "^":
                tokens.append(
                    Token(
                        TokenType.DOTCARET,
                        ".^",
                        self.line,
                        self.column
                    )
                )

                self.advance()
                self.advance()
                continue

            if char == ".":
                tokens.append(
                    Token(
                        TokenType.DOT,
                        ".",
                        self.line,
                        self.column
                    )
                )

                self.advance()
                continue

            # Single-character tokens
            single_char_tokens = {
                "+": TokenType.PLUS,
                "-": TokenType.MINUS,
                "*": TokenType.STAR,
                "/": TokenType.SLASH,
                "^": TokenType.CARET,
                "=": TokenType.EQUAL,
                "'": TokenType.TRANSPOSE,

                "<": TokenType.LT,
                ">": TokenType.GT,
                "~": TokenType.NOT,

                "(": TokenType.LPAREN,
                ")": TokenType.RPAREN,

                "[": TokenType.LBRACKET,
                "]": TokenType.RBRACKET,

                ",": TokenType.COMMA,
                ";": TokenType.SEMICOLON,
                ":": TokenType.COLON,
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

            raise LexerError(
                f"Unexpected character '{char}'",
                line=self.line,
                column=self.column,
                token=char,
            )

        tokens.append(
            Token(TokenType.EOF, None, self.line, self.column)
        )

        return tokens
    
    def string(self):
        start_column = self.column

        # Skip opening quote
        self.advance()

        value = ""

        while (
            not self.is_at_end()
            and self.peek() != '"'
        ):
            value += self.advance()

        if self.is_at_end():
            raise LexerError(
                f"Unterminated string at "
                f"line {self.line}, "
                f"column {start_column}"
            )

        # Skip closing quote
        self.advance()

        return Token(
            TokenType.STRING,
            value,
            self.line,
            start_column
        )

    def single_quoted_string(self):
        start_column = self.column

        # Skip opening quote
        self.advance()

        value = ""

        while not self.is_at_end():
            if self.peek() == "'":
                self.advance()

                return Token(
                    TokenType.STRING,
                    value,
                    self.line,
                    start_column
                )

            value += self.advance()

        raise LexerError(
            f"Unterminated string at "
            f"line {self.line}, "
            f"column {start_column}"
        )

    def number(self):
        start_column = self.column

        if (
            self.peek() == "0"
            and self.peek_next() in {"x", "X", "b", "B"}
        ):
            return self.prefixed_integer_literal()

        number_str = ""

        while not self.is_at_end() and (
            self.peek().isdigit() or self.peek() == "."
        ):
            number_str += self.advance()

        number_value = float(number_str)

        if (
            not self.is_at_end()
            and self.peek() in {"i", "j"}
            and not self.is_identifier_part(self.peek_next())
        ):
            self.advance()

            return Token(
                TokenType.NUMBER,
                complex(0, number_value),
                self.line,
                start_column
            )

        return Token(
            TokenType.NUMBER,
            number_value,
            self.line,
            start_column
        )

    def prefixed_integer_literal(self):
        start_column = self.column
        literal = self.advance()
        literal += self.advance()

        while (
            not self.is_at_end()
            and (
                self.peek().isalnum()
                or self.peek() == "_"
            )
        ):
            literal += self.advance()

        value = parse_numeric_literal(
            literal,
            self.line,
            start_column,
        )

        return Token(
            TokenType.NUMBER,
            value,
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
    
    def peek_next(self):
        if self.position + 1 >= len(self.source):
            return "\0"

        return self.source[self.position + 1]

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

    def is_identifier_part(self, char):
        return char.isalnum() or char == "_"

    def is_single_quoted_string_start(self, tokens):
        if not tokens:
            return True

        return tokens[-1].type in {
            TokenType.EQUAL,
            TokenType.LPAREN,
            TokenType.LBRACKET,
            TokenType.COMMA,
            TokenType.SEMICOLON,
            TokenType.COLON,
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.STAR,
            TokenType.SLASH,
            TokenType.CARET,
            TokenType.DOTSTAR,
            TokenType.DOTSLASH,
            TokenType.DOTCARET,
            TokenType.DOT,
            TokenType.EQEQ,
            TokenType.NEQ,
            TokenType.LT,
            TokenType.GT,
            TokenType.LTE,
            TokenType.GTE,
            TokenType.AND,
            TokenType.OR,
            TokenType.NOT,
            TokenType.IF,
            TokenType.ELSEIF,
            TokenType.RETURN,
            TokenType.BREAK,
            TokenType.CONTINUE,
        }
    
    def skip_comment(self):
        while (
            not self.is_at_end()
            and self.peek() != "\n"
        ):
            self.advance()
