from enum import Enum, auto


class TokenType(Enum):

    # Data
    NUMBER = auto()
    IDENTIFIER = auto()
    STRING = auto()

    # Arithmetic Operators
    PLUS = auto()
    MINUS = auto()
    MUL = auto()
    DIV = auto()

    # Assignment
    ASSIGN = auto()

    # Comparison Operators
    EQ = auto()
    NE = auto()
    LT = auto()
    GT = auto()
    LE = auto()
    GE = auto()

    # Parentheses
    LPAREN = auto()
    RPAREN = auto()

    # Brackets
    LBRACKET = auto()
    RBRACKET = auto()

    # Separators
    SEMICOLON = auto()
    COMMA = auto()

    # Keywords
    IF = auto()
    REPEAT = auto()
    FUNC = auto()
    END = auto()

    # Built-in Functions
    PRINT = auto()
    PRINTLN = auto()
    PRINTTEXT = auto()
    PRINTLNTEXT = auto()

    # End of File
    EOF = auto()

class Token:
    def __init__(self, token_type, value, line, column):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return (
            f"Token("
            f"type={self.type}, "
            f"value={self.value}, "
            f"line={self.line}, "
            f"column={self.column}"
            f")"
        )
"""        
if __name__ == "__main__":

    token = Token(
        TokenType.NUMBER,
        3.14,
        1,
        5
    )

    print(token)
"""