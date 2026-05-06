from core.lexer.token import TokenType
from core.parser.nodes import (
    NumberNode,
    VariableNode,
    BinaryOpNode,
    AssignmentNode,
    CompoundNode,
    PrintNode,
    PrintTextNode
)

class Parser:

    def __init__(self, tokens):

        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[self.position]

    def advance(self):

        self.position += 1

        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None

    def eat(self, token_type):

        if self.current_token.type == token_type:
            self.advance()
        else:
            raise Exception(
                f"Expected {token_type}, "
                f"got {self.current_token.type}"
            )
        
    def factor(self):

        token = self.current_token

        if token.type == TokenType.NUMBER:

            self.eat(TokenType.NUMBER)

            return NumberNode(token.value)

        elif token.type == TokenType.IDENTIFIER:

            self.eat(TokenType.IDENTIFIER)

            return VariableNode(token.value)

        elif token.type == TokenType.LPAREN:

            self.eat(TokenType.LPAREN)

            node = self.expr()

            self.eat(TokenType.RPAREN)

            return node
        
        elif token.type == TokenType.STRING:

            self.eat(TokenType.STRING)

            return token.value

        raise Exception(
            f"Unexpected token {token.type}"
        )
    
    def term(self):

        node = self.factor()

        while self.current_token.type in (
            TokenType.MUL,
            TokenType.DIV
        ):

            operator = self.current_token

            if operator.type == TokenType.MUL:
                self.eat(TokenType.MUL)

            elif operator.type == TokenType.DIV:
                self.eat(TokenType.DIV)

            node = BinaryOpNode(
                left=node,
                operator=operator.type,
                right=self.factor()
            )

        return node
    
    def expr(self):

        node = self.term()

        while self.current_token.type in (
            TokenType.PLUS,
            TokenType.MINUS
        ):

            operator = self.current_token

            if operator.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)

            elif operator.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)

            node = BinaryOpNode(
                left=node,
                operator=operator.type,
                right=self.term()
            )

        return node
    
    def assignment(self):

        variable_token = self.current_token

        self.eat(TokenType.IDENTIFIER)

        self.eat(TokenType.ASSIGN)

        value_node = self.expr()

        return AssignmentNode(
            variable=VariableNode(variable_token.value),
            value=value_node
        )

    def print_statement(self):

        newline = False

        if self.current_token.type == TokenType.PRINT:
            self.eat(TokenType.PRINT)

        elif self.current_token.type == TokenType.PRINTLN:
            newline = True
            self.eat(TokenType.PRINTLN)

        self.eat(TokenType.LPAREN)

        expression = self.expr()

        self.eat(TokenType.RPAREN)

        return PrintNode(
            expression,
            newline
        )

    def print_text_statement(self):

        newline = False

        if self.current_token.type == TokenType.PRINTTEXT:
            self.eat(TokenType.PRINTTEXT)

        elif self.current_token.type == TokenType.PRINTLNTEXT:
            newline = True
            self.eat(TokenType.PRINTLNTEXT)

        self.eat(TokenType.LPAREN)

        token = self.current_token

        self.eat(TokenType.STRING)

        self.eat(TokenType.RPAREN)

        return PrintTextNode(
            token.value,
            newline
        )
    
    def statement(self):

        if self.current_token.type == TokenType.IDENTIFIER:
            return self.assignment()

        elif self.current_token.type in (
            TokenType.PRINT,
            TokenType.PRINTLN
        ):
            return self.print_statement()

        elif self.current_token.type in (
            TokenType.PRINTTEXT,
            TokenType.PRINTLNTEXT
        ):
            return self.print_text_statement()

        return self.expr()
    
    def parse(self):

        program = CompoundNode()

        while self.current_token.type != TokenType.EOF:

            statement = self.statement()

            program.add(statement)

            self.eat(TokenType.SEMICOLON)

        return program

"""    
if __name__ == "__main__":

    from core.lexer.lexer import Lexer

    source = "
    A = 2 + 3 * 4;
    B = A + 10;
    "

    lexer = Lexer(source)

    tokens = lexer.tokenize()

    parser = Parser(tokens)

    ast = parser.parse()

    print(ast)    
"""