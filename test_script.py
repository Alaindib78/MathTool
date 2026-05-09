from core.lexer.lexer import Lexer
from core.parser.parser import Parser
from core.interpreter.interpreter import Interpreter
from core.runtime.context import RuntimeContext


source = """
A = 5;
B = A * 2;
C = B + 1;
C;
"""

lexer = Lexer(source)
tokens = lexer.tokenize()

parser = Parser(tokens)
ast = parser.parse()

print(ast)

context = RuntimeContext()

interpreter = Interpreter(context)

result = interpreter.evaluate(ast)

print("\nResult:", result)

print("\nWorkspace:")
print(context.variables)