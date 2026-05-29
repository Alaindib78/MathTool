import pytest
import numpy as np

from core.errors.errors import LexerError
from core.lexer.lexer import Lexer
from core.lexer.token import TokenType


def test_tokenizes_keywords_operators_strings_and_skips_comments():
    source = '''
if A >= 10 && B ~= "done" % ignore this comment
    value = A ./ 2 .^ 3;
end
'''

    tokens = Lexer(source).tokenize()

    assert [token.type for token in tokens] == [
        TokenType.IF,
        TokenType.IDENTIFIER,
        TokenType.GTE,
        TokenType.NUMBER,
        TokenType.AND,
        TokenType.IDENTIFIER,
        TokenType.NEQ,
        TokenType.STRING,
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.IDENTIFIER,
        TokenType.DOTSLASH,
        TokenType.NUMBER,
        TokenType.DOTCARET,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.END,
        TokenType.EOF,
    ]
    assert tokens[7].value == "done"
    assert tokens[9].value == "="
    assert tokens[-1].value is None


def test_lexer_reports_unexpected_character_location():
    with pytest.raises(LexerError) as error:
        Lexer("A = ?").tokenize()

    assert error.value.line == 1
    assert error.value.column == 5
    assert error.value.token == "?"


def test_lexer_tokenizes_anonymous_function_marker():
    tokens = Lexer("f = @(x) x.^2;").tokenize()

    assert [token.type for token in tokens[:7]] == [
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.AT,
        TokenType.LPAREN,
        TokenType.IDENTIFIER,
        TokenType.RPAREN,
        TokenType.IDENTIFIER,
    ]


def test_lexer_tokenizes_matlab_not_operators():
    tokens = Lexer("A = ~false; B = 1 ~= 2; C = A & B | A;").tokenize()

    assert [token.type for token in tokens] == [
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.NOT,
        TokenType.FALSE,
        TokenType.SEMICOLON,
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.NUMBER,
        TokenType.NEQ,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.IDENTIFIER,
        TokenType.AND,
        TokenType.IDENTIFIER,
        TokenType.OR,
        TokenType.IDENTIFIER,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]
    assert tokens[2].value == "~"
    assert tokens[8].value == "~="
    assert tokens[14].value == "&"
    assert tokens[16].value == "|"


def test_lexer_tokenizes_loop_control_keywords():
    tokens = Lexer("break; continue; return;").tokenize()

    assert [token.type for token in tokens] == [
        TokenType.BREAK,
        TokenType.SEMICOLON,
        TokenType.CONTINUE,
        TokenType.SEMICOLON,
        TokenType.RETURN,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]


def test_lexer_tokenizes_imaginary_number_suffixes():
    tokens = Lexer("z = 1 + 2i; w = 3j;").tokenize()

    assert [token.type for token in tokens] == [
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.NUMBER,
        TokenType.PLUS,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]
    assert tokens[4].value == 2j
    assert tokens[8].value == 3j


def test_lexer_tokenizes_hexadecimal_and_binary_integer_literals():
    tokens = Lexer(
        "A = 0x2A; B = 0X2A; C = 0b101010; D = 0B101010;"
    ).tokenize()

    values = [
        token.value
        for token in tokens
        if token.type == TokenType.NUMBER
    ]

    assert values == [42, 42, 42, 42]
    assert all(isinstance(value, int) for value in values)


def test_lexer_tokenizes_typed_integer_literals():
    tokens = Lexer(
        "A = 0xFFu8; B = 0xFFs8; C = 0b1111111111111111s16;"
    ).tokenize()

    values = [
        token.value
        for token in tokens
        if token.type == TokenType.NUMBER
    ]

    assert values[0] == np.uint8(255)
    assert isinstance(values[0], np.uint8)
    assert values[1] == np.int8(-1)
    assert isinstance(values[1], np.int8)
    assert values[2] == np.int16(-1)
    assert isinstance(values[2], np.int16)


@pytest.mark.parametrize(
    "source, token",
    [
        ("A = 0x;", "0x"),
        ("A = 0b;", "0b"),
        ("A = 0xG1;", "0xG1"),
        ("A = 0b102;", "0b102"),
        ("A = 0x2Au128;", "0x2Au128"),
        ("A = 0x2As7;", "0x2As7"),
    ],
)
def test_lexer_rejects_invalid_prefixed_integer_literals(source, token):
    with pytest.raises(LexerError) as error:
        Lexer(source).tokenize()

    assert error.value.line == 1
    assert error.value.column == 5
    assert error.value.token == token
    assert "Invalid" in str(error.value)


def test_lexer_tokenizes_dot_access_without_breaking_decimals_or_elementwise_ops():
    tokens = Lexer("s.x = 3.14; B = A .* 2;").tokenize()

    assert [token.type for token in tokens] == [
        TokenType.IDENTIFIER,
        TokenType.DOT,
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.IDENTIFIER,
        TokenType.DOTSTAR,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]
    assert tokens[4].value == 3.14


def test_lexer_distinguishes_single_quoted_strings_from_transpose():
    tokens = Lexer("f = sym('x'); T = M';").tokenize()

    assert [token.type for token in tokens] == [
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.IDENTIFIER,
        TokenType.LPAREN,
        TokenType.STRING,
        TokenType.RPAREN,
        TokenType.SEMICOLON,
        TokenType.IDENTIFIER,
        TokenType.EQUAL,
        TokenType.IDENTIFIER,
        TokenType.TRANSPOSE,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]
    assert tokens[4].value == "x"


def test_lexer_rejects_unterminated_string():
    with pytest.raises(LexerError) as error:
        Lexer('message = "unterminated').tokenize()

    assert "Unterminated string" in str(error.value)
