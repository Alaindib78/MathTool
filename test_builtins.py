from core.lexer.lexer import Lexer
from core.parser.parser import Parser
from core.interpreter.interpreter import Interpreter
from core.runtime.context import RuntimeContext


source = """
A = sqrt(16);
B = sin(0);
C = zeros(5);

print(A);
print(B);
print(C);
"""

lexer = Lexer(source)
tokens = lexer.tokenize()

parser = Parser(tokens)
ast = parser.parse()

context = RuntimeContext()

interpreter = Interpreter(context)

interpreter.evaluate(ast)

print("\nWorkspace:")
print(context.variables)