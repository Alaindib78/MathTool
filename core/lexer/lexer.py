from core.lexer.token import Token, TokenType

class Lexer:

    def __init__(self, text):

        self.text = text
        self.position = 0
        self.line = 1
        self.column = 1

        self.current_char = (
            self.text[self.position]
            if self.text
            else None
        )

    def advance(self):

        if self.current_char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        self.position += 1

        if self.position >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.position]

    def skip_whitespace(self):

        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    
    def number(self):

        result = ""
        line = self.line
        column = self.column

        dot_count = 0

        while (
            self.current_char is not None
            and (
                self.current_char.isdigit()
                or self.current_char == "."
            )
        ):

            if self.current_char == ".":
                dot_count += 1

                if dot_count > 1:
                    raise Exception(
                        f"Invalid number at line {line}"
                    )

            result += self.current_char
            self.advance()

        return Token(
            TokenType.NUMBER,
            float(result),
            line,
            column
        ) 

    def identifier(self):

        result = ""
        line = self.line
        column = self.column

        while (
            self.current_char is not None
            and (
                self.current_char.isalnum()
                or self.current_char == "_"
            )
        ):

            result += self.current_char
            self.advance()

        keywords = {
            "if": TokenType.IF,
            "repeat": TokenType.REPEAT,
            "func": TokenType.FUNC,
            "end": TokenType.END,

            "print": TokenType.PRINT,
            "println": TokenType.PRINTLN,
            "printtext": TokenType.PRINTTEXT,
            "printlntext": TokenType.PRINTLNTEXT,
        }

        token_type = keywords.get(
            result,
            TokenType.IDENTIFIER
        )

        return Token(
            token_type,
            result,
            line,
            column
        )   
    def get_next_token(self):

        while self.current_char is not None:

            # Skip whitespace
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            # Numbers
            if self.current_char.isdigit():
                return self.number()

            # Identifiers
            if self.current_char.isalpha():
                return self.identifier()

            # Operators
            if self.current_char == "+":
                token = Token(
                    TokenType.PLUS,
                    "+",
                    self.line,
                    self.column
                )
                self.advance()
                return token

            if self.current_char == "-":
                token = Token(
                    TokenType.MINUS,
                    "-",
                    self.line,
                    self.column
                )
                self.advance()
                return token

            if self.current_char == "*":
                token = Token(
                    TokenType.MUL,
                    "*",
                    self.line,
                    self.column
                )
                self.advance()
                return token

            if self.current_char == "/":
                token = Token(
                    TokenType.DIV,
                    "/",
                    self.line,
                    self.column
                )
                self.advance()
                return token

            if self.current_char == "=":
                token = Token(
                    TokenType.ASSIGN,
                    "=",
                    self.line,
                    self.column
                )
                self.advance()
                return token

            if self.current_char == ";":
                token = Token(
                    TokenType.SEMICOLON,
                    ";",
                    self.line,
                    self.column
                )
                self.advance()
                return token

            if self.current_char == "(":
                token = Token(
                    TokenType.LPAREN,
                    "(",
                    self.line,
                    self.column
                )
                self.advance()
                return token

            if self.current_char == ")":
                token = Token(
                    TokenType.RPAREN,
                    ")",
                    self.line,
                    self.column
                )
                self.advance()
                return token

            raise Exception(
                f"Invalid character '{self.current_char}' "
                f"at line {self.line}, column {self.column}"
            )

        return Token(
            TokenType.EOF,
            None,
            self.line,
            self.column
        )
    
    def tokenize(self):

        tokens = []

        while True:

            token = self.get_next_token()
            tokens.append(token)

            if token.type == TokenType.EOF:
                break

        return tokens

"""    
if __name__ == "__main__":

    source = "
    A = 2 + 3 * 4;
    print(A);
    end;
    "

    lexer = Lexer(source)

    tokens = lexer.tokenize()

    for token in tokens:
        print(token)
"""