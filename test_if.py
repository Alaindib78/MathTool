from core.lexer.lexer import Lexer
from core.parser.parser import Parser
from core.interpreter.interpreter import Interpreter
from core.runtime.context import RuntimeContext


source = """
A = 3;

if A > 10
    B = 100;
elseif A > 5
    B = 50;
else
    B = 0;
end

B;
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