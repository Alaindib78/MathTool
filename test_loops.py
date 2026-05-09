from core.lexer.lexer import Lexer
from core.parser.parser import Parser
from core.interpreter.interpreter import Interpreter
from core.runtime.context import RuntimeContext


source = """
sum = 0;

for i = 1:5
    sum = sum + i;
end

x = 0;

while x < 3
    x = x + 1;
end
"""

lexer = Lexer(source)
tokens = lexer.tokenize()

parser = Parser(tokens)
ast = parser.parse()

context = RuntimeContext()

interpreter = Interpreter(context)

interpreter.evaluate(ast)

print(context.variables)