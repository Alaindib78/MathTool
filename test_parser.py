from core.lexer.lexer import Lexer
from core.parser.parser import Parser


source = "A = 2 + 3 * 4"

lexer = Lexer(source)
tokens = lexer.tokenize()

parser = Parser(tokens)

ast = parser.parse()

print(ast)