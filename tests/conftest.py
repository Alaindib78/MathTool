import pytest

from core.interpreter.interpreter import Interpreter
from core.lexer.lexer import Lexer
from core.parser.parser import Parser
from core.runtime.context import RuntimeContext
from core.semantic.semantic_analyzer import SemanticAnalyzer


def parse_source(source):
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()


def execute_source(source, *, analyze=False, context=None):
    ast = parse_source(source)

    if analyze:
        SemanticAnalyzer().analyze(ast)

    context = context or RuntimeContext()
    result = Interpreter(context).evaluate(ast)
    return result, context


@pytest.fixture
def parse():
    return parse_source


@pytest.fixture
def execute():
    return execute_source
