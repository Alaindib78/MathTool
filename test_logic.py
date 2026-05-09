from core.lexer.lexer import Lexer
from core.parser.parser import Parser
from core.interpreter.interpreter import Interpreter
from core.runtime.context import RuntimeContext


source = """
A = 5 > 3;
B = 10 == 10;
C = A && B;
D = !(5 < 2);
"""

lexer = Lexer(source)
tokens = lexer.tokenize()

parser = Parser(tokens)
ast = parser.parse()

context = RuntimeContext()

interpreter = Interpreter(context)

interpreter.evaluate(ast)

print(context.variables)