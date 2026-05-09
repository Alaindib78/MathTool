from core.lexer.lexer import Lexer
from core.parser.parser import Parser
from core.interpreter.interpreter import Interpreter
from core.runtime.context import RuntimeContext


source = """
A = 2 + 3 * 4
"""

lexer = Lexer(source)
tokens = lexer.tokenize()

parser = Parser(tokens)
ast = parser.parse()

context = RuntimeContext()

interpreter = Interpreter(context)

result = interpreter.evaluate(ast)

print("Result:", result)

print("Variables:", context.variables)