from core.lexer import token
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
    MatrixNode,
    ForNode,
    FunctionCallNode,
    FunctionDeclarationNode,
    ReturnNode,
    SymsNode,
    TransposeNode,
)
from core.errors.errors import ParserError


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
        
        if self.match(TokenType.FUNCTION):
            return self.function_declaration()

        if self.match(TokenType.RETURN):
            return self.return_statement()

        if self.is_syms_statement():
            return self.syms_statement()

        # Assignment
        if self.is_assignment_start():
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
            IdentifierNode(variable.value, variable.line, variable.column),
            iterable,
            body,
            variable.line,
            variable.column
        )

    def assignment(self):
        target = self.assignment_target()
        self.consume(TokenType.EQUAL)

        value = self.expression()

        return AssignmentNode(
            target,
            value,
            target.line,
            target.column
        )

    def assignment_target(self):
        identifier = self.consume(TokenType.IDENTIFIER)

        target = IdentifierNode(
            identifier.value,
            identifier.line,
            identifier.column
        )

        if not self.match(TokenType.LPAREN):
            return target

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
            arguments,
            identifier.line,
            identifier.column
        )

    def expression(self):
        return self.range_expression()

    def range_expression(self):
        start = self.logical_or()

        if self.match(TokenType.COLON):
            middle = self.logical_or()

            if self.match(TokenType.COLON):
                end = self.logical_or()
                colon = self.previous()

                return RangeNode(
                    start,
                    middle,
                    end,
                    colon.line,
                    colon.column
                )
            
            colon = self.previous()

            return RangeNode(
                start,
                NumberNode(1),
                middle,
                colon.line,
                colon.column
            )

        return start
    
    def return_statement(self):
        value = self.expression()

        return ReturnNode(value)

    def syms_statement(self):
        command = self.consume(TokenType.IDENTIFIER)

        names = []

        while (
            self.check(TokenType.IDENTIFIER)
            and self.peek().line == command.line
        ):
            names.append(self.advance().value)

            if (
                self.check(TokenType.COMMA)
                and self.peek().line == command.line
            ):
                self.advance()

        if not names:
            raise ParserError(
                "Expected symbolic variable name",
                line=command.line,
                column=command.column,
                token=command.value,
            )

        return SymsNode(
            names,
            command.line,
            command.column
        )
    
    def function_declaration(self):
        return_variable = None

        # Optional return variable
        if self.check(TokenType.IDENTIFIER):
            identifier = self.advance()

            if self.match(TokenType.EQUAL):
                return_variable = identifier.value

                function_name = self.consume(
                    TokenType.IDENTIFIER
                )

            else:
                function_name = identifier

        else:
            raise Exception(
                "Expected function name"
            )

        self.consume(TokenType.LPAREN)

        parameters = []

        if not self.check(TokenType.RPAREN):
            param = self.consume(
                TokenType.IDENTIFIER
            )

            parameters.append(param.value)

            while self.match(TokenType.COMMA):
                param = self.consume(
                    TokenType.IDENTIFIER
                )

                parameters.append(param.value)

        self.consume(TokenType.RPAREN)

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

        return FunctionDeclarationNode(
            function_name.value,
            parameters,
            body,
            return_variable
        )

    def logical_or(self):
        node = self.logical_and()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logical_and()

            node = BinaryOpNode(
                node,
                operator.type,
                right,
                operator.line,
                operator.column
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
                right,
                operator.line,
                operator.column
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
                right,
                operator.line, 
                operator.column
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
                right,
                operator.line,
                operator.column
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
                right,
                operator.line,
                operator.column
            )

        return node

    def factor(self):
        node = self.power()

        while self.match(
            TokenType.STAR,
            TokenType.SLASH,
            TokenType.MODULO,
            TokenType.DOTSTAR,
            TokenType.DOTSLASH
        ):
            operator = self.previous()
            right = self.power()

            node = BinaryOpNode(
                node,
                operator.type,
                right,
                operator.line,
                operator.column
            )

        return node

    def power(self):
        node = self.unary()

        while self.match(
            TokenType.CARET,
            TokenType.DOTCARET
        ):
            operator = self.previous()
            right = self.unary()

            node = BinaryOpNode(
                node,
                operator.type,
                right,
                operator.line,
                operator.column
            )

        return node
    
    def postfix(self):
        expr = self.primary()

        while self.match(TokenType.TRANSPOSE):
            operator = self.previous()
            expr = TransposeNode(expr, operator.line, operator.column)

        return expr

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
                operand,
                operator.line,
                operator.column
            )

        return self.postfix()

    def primary(self):
        if self.match(TokenType.STRING):
            token = self.previous()

            return StringNode(token.value, token.line, token.column)
        
        if self.match(TokenType.NUMBER):
            token = self.previous()

            return NumberNode(token.value,token.line, token.column )
        
        if self.match(TokenType.TRUE):
            token = self.previous()
            return NumberNode(True, token.line, token.column)

        if self.match(TokenType.FALSE):
            token = self.previous()
            return NumberNode(False, token.line, token.column)

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

                # Indexing if variable exists syntax-style
#                if len(arguments) > 0:
#                    return IndexNode(
#                        IdentifierNode(identifier.value),
#                        arguments
#                    )

                return FunctionCallNode(
                    identifier.value,
                    arguments,
                    identifier.line,
                    identifier.column
                )

            return IdentifierNode(identifier.value, identifier.line, identifier.column)
        
        if self.match(TokenType.LBRACKET):
            return self.matrix_literal()

        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.consume(TokenType.RPAREN)
            return expr

        token = self.peek()

        raise ParserError(
            "Unexpected token",
            line=token.line,
            column=token.column,
            token=token.value,
        )
    
    def matrix_literal(self):
        rows = []

        current_row = []

        while (
            not self.check(TokenType.RBRACKET)
            and not self.is_at_end()
        ):
            # -----------------------------
            # Matrix element
            # -----------------------------

            value = self.matrix_expression()

            current_row.append(value)

            # -----------------------------
            # Comma-separated
            # -----------------------------

            if self.match(TokenType.COMMA):
                continue

            # -----------------------------
            # Row separator
            # -----------------------------

            if self.match(TokenType.SEMICOLON):
                rows.append(current_row)

                current_row = []

                continue

            # -----------------------------
            # Stop row on closing bracket
            # -----------------------------

            if self.check(TokenType.RBRACKET):
                break

            # -----------------------------
            # MATLAB whitespace-separated
            # elements
            # -----------------------------

            next_token = self.peek()

            if next_token.type in (
                TokenType.NUMBER,
                TokenType.IDENTIFIER,
                TokenType.MINUS,
                TokenType.STRING,
                TokenType.LPAREN,
            ):
                continue

        if current_row:
            rows.append(current_row)

        self.consume(TokenType.RBRACKET)

        token = self.previous()

        return MatrixNode(rows, token.line, token.column)    
    
    def matrix_expression(self):
        # Unary negative literal
        if self.match(TokenType.MINUS):
            operand = self.postfix()

            return UnaryOpNode(
                TokenType.MINUS,
                operand
            )

        return self.postfix()

    def matrix_element(self):
        # Unary minus support
        if self.match(TokenType.MINUS):
            operand = self.primary()

            return UnaryOpNode(
                TokenType.MINUS,
                operand
            )

        return self.expression()
    
    # Utility methods

    def match(self, *types):
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True

        return False

    def is_assignment_start(self):
        if self.peek().type != TokenType.IDENTIFIER:
            return False

        if self.peek_next().type == TokenType.EQUAL:
            return True

        if self.peek_next().type != TokenType.LPAREN:
            return False

        depth = 0
        position = self.position + 1

        while position < len(self.tokens):
            token_type = self.tokens[position].type

            if token_type == TokenType.LPAREN:
                depth += 1
            elif token_type == TokenType.RPAREN:
                depth -= 1

                if depth == 0:
                    next_position = position + 1

                    if next_position >= len(self.tokens):
                        return False

                    return (
                        self.tokens[next_position].type
                        == TokenType.EQUAL
                    )
            elif token_type == TokenType.EOF:
                return False

            position += 1

        return False

    def is_syms_statement(self):
        return (
            self.peek().type == TokenType.IDENTIFIER
            and self.peek().value == "syms"
            and self.peek_next().type == TokenType.IDENTIFIER
            and self.peek_next().type != TokenType.EQUAL
        )

    def consume(self, token_type):
        if self.check(token_type):
            return self.advance()

        token = self.peek()

        raise ParserError(
            f"Expected token {token_type}, "
            f"got {token.type}",
            line=token.line,
            column=token.column,
            token=token.value,
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
