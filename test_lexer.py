from core.lexer.lexer import Lexer


source = """
A = 5 + 3;
B = A * 10;
"""

lexer = Lexer(source)

tokens = lexer.tokenize()

for token in tokens:
    print(token)