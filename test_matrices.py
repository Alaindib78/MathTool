from core.lexer.lexer import Lexer
from core.parser.parser import Parser
from core.interpreter.interpreter import Interpreter
from core.runtime.context import RuntimeContext


source = """
A = [1 2 3];
B = [4 5 6];

C = A .* B;

M = [1 2;
     3 4];

x = M(2,1);
"""

lexer = Lexer(source)
tokens = lexer.tokenize()

parser = Parser(tokens)
ast = parser.parse()

context = RuntimeContext()

interpreter = Interpreter(context)

interpreter.evaluate(ast)

for k, v in context.variables.items():
    print(k, "=", v)