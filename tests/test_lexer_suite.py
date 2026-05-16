import pytest

from core.errors.errors import LexerError
from core.lexer.lexer import Lexer
from core.lexer.token import TokenType


def test_tokenizes_keywords_operators_strings_and_skips_comments():
    source = '''
if A >= 10 && B != "done" % ignore this comment
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
        Lexer("A = @").tokenize()

    assert error.value.line == 1
    assert error.value.column == 5
    assert error.value.token == "@"


def test_lexer_rejects_unterminated_string():
    with pytest.raises(LexerError) as error:
        Lexer('message = "unterminated').tokenize()

    assert "Unterminated string" in str(error.value)
