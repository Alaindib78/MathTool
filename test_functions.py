from core.lexer.lexer import Lexer
from core.parser.parser import Parser
from core.interpreter.interpreter import Interpreter
from core.runtime.context import RuntimeContext


source = """
function y = square(x)
    y = x ^ 2;
end

function z = add(a, b)
    z = a + b;
end

A = square(5);

B = add(10, 20);

print(A);

print(B);
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