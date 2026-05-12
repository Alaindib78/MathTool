from enum import Enum, auto

class TokenType(Enum):
    # Special
    EOF = auto()

    # Literals
    NUMBER = auto()
    IDENTIFIER = auto()
    STRING = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    CARET = auto()
    MODULO = auto()
    TRANSPOSE = auto()

    DOTSTAR = auto()
    DOTSLASH = auto()
    DOTCARET = auto()

    # Assignment
    EQUAL = auto()

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()

    LBRACKET = auto()
    RBRACKET = auto()

    COMMA = auto()
    SEMICOLON = auto()
    COLON = auto()

    # Comparison
    EQEQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LTE = auto()
    GTE = auto()

    # Logical
    AND = auto()
    OR = auto()
    NOT = auto()

    # Keywords
    IF = auto()
    ELSE = auto()
    ELSEIF = auto()
    END = auto()

    FOR = auto()
    WHILE = auto()

    FUNCTION = auto()
    RETURN = auto()

    TRUE = auto()
    FALSE = auto()

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
    