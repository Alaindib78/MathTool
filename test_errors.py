from core.lexer.lexer import Lexer
from core.parser.parser import Parser
from core.semantic.semantic_analyzer import (
    SemanticAnalyzer
)
from core.interpreter.interpreter import (
    Interpreter
)
from core.runtime.context import RuntimeContext


source = """
A = 5 / 0;
"""

lexer = Lexer(source)

tokens = lexer.tokenize()

parser = Parser(tokens)

ast = parser.parse()

semantic = SemanticAnalyzer()

semantic.analyze(ast)

context = RuntimeContext()

interpreter = Interpreter(context)

interpreter.evaluate(ast)