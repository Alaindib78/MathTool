from core.lexer.token import TokenType

from core.ast.nodes import (
    ProgramNode,
    NumberNode,
    StringNode,
    IdentifierNode,
    BinaryOpNode,
    UnaryOpNode,
    AssignmentNode,
    IfNode,
    WhileNode,
    RangeNode,
    ForNode,
    FunctionCallNode,
)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def parse(self):
        statements = []

        while not self.is_at_end():
            # Skip stray semicolons
            while self.match(TokenType.SEMICOLON):
                pass

            if self.is_at_end():
                break

            stmt = self.statement()

            statements.append(stmt)

            # Optional semicolon
            self.match(TokenType.SEMICOLON)

        return ProgramNode(statements)

    def statement(self):
        # If statement
        if self.match(TokenType.IF):
            return self.if_statement()
        
        if self.match(TokenType.WHILE):
            return self.while_statement()

        if self.match(TokenType.FOR):
            return self.for_statement()

        # Assignment
        if (
            self.peek().type == TokenType.IDENTIFIER
            and self.peek_next().type == TokenType.EQUAL
        ):
            return self.assignment()

        return self.expression()
    
    def if_statement(self):
        condition = self.expression()

        then_branch = []

        while (
            not self.check(TokenType.ELSEIF)
            and not self.check(TokenType.ELSE)
            and not self.check(TokenType.END)
            and not self.is_at_end()
        ):
            while self.match(TokenType.SEMICOLON):
                pass

            if (
                self.check(TokenType.ELSEIF)
                or self.check(TokenType.ELSE)
                or self.check(TokenType.END)
            ):
                break

            then_branch.append(self.statement())

            self.match(TokenType.SEMICOLON)

        elseif_branches = []

        while self.match(TokenType.ELSEIF):
            elseif_condition = self.expression()

            elseif_body = []

            while (
                not self.check(TokenType.ELSEIF)
                and not self.check(TokenType.ELSE)
                and not self.check(TokenType.END)
                and not self.is_at_end()
            ):
                while self.match(TokenType.SEMICOLON):
                    pass

                if (
                    self.check(TokenType.ELSEIF)
                    or self.check(TokenType.ELSE)
                    or self.check(TokenType.END)
                ):
                    break

                elseif_body.append(self.statement())

                self.match(TokenType.SEMICOLON)

            elseif_branches.append(
                (elseif_condition, elseif_body)
            )

        else_branch = None

        if self.match(TokenType.ELSE):
            else_branch = []

            while (
                not self.check(TokenType.END)
                and not self.is_at_end()
            ):
                while self.match(TokenType.SEMICOLON):
                    pass

                if self.check(TokenType.END):
                    break

                else_branch.append(self.statement())

                self.match(TokenType.SEMICOLON)

        self.consume(TokenType.END)

        return IfNode(
            condition,
            then_branch,
            elseif_branches,
            else_branch
        )
    
    def while_statement(self):
        condition = self.expression()

        body = []

        while (
            not self.check(TokenType.END)
            and not self.is_at_end()
        ):
            while self.match(TokenType.SEMICOLON):
                pass

            if self.check(TokenType.END):
                break

            body.append(self.statement())

            self.match(TokenType.SEMICOLON)

        self.consume(TokenType.END)

        return WhileNode(condition, body)
    
    def for_statement(self):
        variable = self.consume(
            TokenType.IDENTIFIER
        )

        self.consume(TokenType.EQUAL)

        iterable = self.range_expression()

        body = []

        while (
            not self.check(TokenType.END)
            and not self.is_at_end()
        ):
            while self.match(TokenType.SEMICOLON):
                pass

            if self.check(TokenType.END):
                break

            body.append(self.statement())

            self.match(TokenType.SEMICOLON)

        self.consume(TokenType.END)

        return ForNode(
            IdentifierNode(variable.value),
            iterable,
            body
        )

    def assignment(self):
        identifier = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.EQUAL)

        value = self.expression()

        return AssignmentNode(
            IdentifierNode(identifier.value),
            value
        )

    def expression(self):
        return self.range_expression()
#        return self.term()

    def range_expression(self):
        start = self.logical_or()

        if self.match(TokenType.COLON):
            middle = self.logical_or()

            if self.match(TokenType.COLON):
                end = self.logical_or()

                return RangeNode(
                    start,
                    middle,
                    end
                )

            return RangeNode(
                start,
                NumberNode(1),
                middle
            )

        return start

    def logical_or(self):
        node = self.logical_and()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logical_and()

            node = BinaryOpNode(
                node,
                operator.type,
                right
            )

        return node


    def logical_and(self):
        node = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()

            node = BinaryOpNode(
                node,
                operator.type,
                right
            )

        return node


    def equality(self):
        node = self.comparison()

        while self.match(
            TokenType.EQEQ,
            TokenType.NEQ
        ):
            operator = self.previous()
            right = self.comparison()

            node = BinaryOpNode(
                node,
                operator.type,
                right
            )

        return node


    def comparison(self):
        node = self.term()

        while self.match(
            TokenType.LT,
            TokenType.GT,
            TokenType.LTE,
            TokenType.GTE
        ):
            operator = self.previous()
            right = self.term()

            node = BinaryOpNode(
                node,
                operator.type,
                right
            )

        return node
    
    def term(self):
        node = self.factor()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.factor()

            node = BinaryOpNode(
                node,
                operator.type,
                right
            )

        return node

    def factor(self):
        node = self.power()

        while self.match(
            TokenType.STAR,
            TokenType.SLASH,
            TokenType.MODULO
        ):
            operator = self.previous()
            right = self.power()

            node = BinaryOpNode(
                node,
                operator.type,
                right
            )

        return node

    def power(self):
        node = self.unary()

        while self.match(TokenType.CARET):
            operator = self.previous()
            right = self.unary()

            node = BinaryOpNode(
                node,
                operator.type,
                right
            )

        return node

    def unary(self):
        if self.match(
            TokenType.MINUS,
            TokenType.PLUS,
            TokenType.NOT
        ):
            operator = self.previous()

            operand = self.unary()

            return UnaryOpNode(
                operator.type,
                operand
            )

        return self.primary()

    def primary(self):
        if self.match(TokenType.STRING):
            return StringNode(self.previous().value)
        
        if self.match(TokenType.NUMBER):
            return NumberNode(self.previous().value)
        
        if self.match(TokenType.TRUE):
            return NumberNode(True)

        if self.match(TokenType.FALSE):
            return NumberNode(False)

#        if self.match(TokenType.IDENTIFIER):
#            return IdentifierNode(self.previous().value)

        if self.match(TokenType.IDENTIFIER):
            identifier = self.previous()

            # Function call
            if self.match(TokenType.LPAREN):
                arguments = []

                if not self.check(TokenType.RPAREN):
                    arguments.append(
                        self.expression()
                    )

                while self.match(TokenType.COMMA):
                    arguments.append(
                        self.expression()
                    )

                self.consume(TokenType.RPAREN)

                return FunctionCallNode(
                    identifier.value,
                    arguments
                )

            return IdentifierNode(identifier.value)

        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.consume(TokenType.RPAREN)
            return expr

        raise Exception(
            f"Unexpected token: {self.peek()}"
        )

    # Utility methods

    def match(self, *types):
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True

        return False

    def consume(self, token_type):
        if self.check(token_type):
            return self.advance()

        raise Exception(
            f"Expected token {token_type}, "
            f"got {self.peek().type}"
        )

    def check(self, token_type):
        if self.is_at_end():
            return False

        return self.peek().type == token_type

    def advance(self):
        if not self.is_at_end():
            self.position += 1

        return self.previous()

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.position]

    def peek_next(self):
        if self.position + 1 >= len(self.tokens):
            return self.tokens[-1]

        return self.tokens[self.position + 1]

    def previous(self):
        return self.tokens[self.position - 1]