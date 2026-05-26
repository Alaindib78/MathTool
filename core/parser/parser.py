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
    MultiAssignmentTargetNode,
    IfNode,
    WhileNode,
    RangeNode,
    MatrixNode,
    ForNode,
    FunctionCallNode,
    FieldAccessNode,
    IndexAccessNode,
    NameValueNode,
    FunctionDeclarationNode,
    ReturnNode,
    BreakNode,
    ContinueNode,
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

        if self.match(TokenType.BREAK):
            return self.break_statement()

        if self.match(TokenType.CONTINUE):
            return self.continue_statement()

        if self.is_syms_statement():
            return self.syms_statement()

        if self.is_help_statement():
            return self.help_statement()

        if self.is_lookfor_statement():
            return self.lookfor_statement()

        if self.is_cwd_statement():
            return self.cwd_statement()

        if self.is_who_statement():
            return self.who_statement()

        if self.is_figure_statement():
            return self.figure_statement()

        if self.is_close_statement():
            return self.close_statement()

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
        if self.match(TokenType.LBRACKET):
            bracket = self.previous()
            targets = []

            if self.check(TokenType.RBRACKET):
                raise ParserError(
                    "Expected assignment target",
                    line=bracket.line,
                    column=bracket.column,
                    token=bracket.value,
                )

            targets.append(
                self.assignment_target_identifier()
            )

            while not self.check(TokenType.RBRACKET):
                self.match(TokenType.COMMA)

                targets.append(
                    self.assignment_target_identifier()
                )

            self.consume(TokenType.RBRACKET)

            return MultiAssignmentTargetNode(
                targets,
                bracket.line,
                bracket.column,
            )

        return self.single_assignment_target()

    def assignment_target_identifier(self):
        identifier = self.consume(TokenType.IDENTIFIER)

        return IdentifierNode(
            identifier.value,
            identifier.line,
            identifier.column
        )

    def single_assignment_target(self):
        identifier = self.consume(TokenType.IDENTIFIER)

        target = IdentifierNode(
            identifier.value,
            identifier.line,
            identifier.column
        )

        return self.assignment_target_postfix(target)

    def assignment_target_postfix(self, target):
        while True:
            if self.match(TokenType.LPAREN):
                paren = self.previous()
                arguments = self.function_arguments()

                self.consume(TokenType.RPAREN)

                if isinstance(target, IdentifierNode):
                    target = FunctionCallNode(
                        target.name,
                        arguments,
                        target.line,
                        target.column,
                    )
                else:
                    target = IndexAccessNode(
                        target,
                        arguments,
                        paren.line,
                        paren.column,
                    )

                continue

            if self.match(TokenType.DOT):
                dot = self.previous()
                field = self.consume(TokenType.IDENTIFIER)

                target = FieldAccessNode(
                    target,
                    field.value,
                    dot.line,
                    dot.column,
                )

                continue

            return target

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
        command = self.previous()
        value = None

        if not self.is_statement_boundary(command.line):
            value = self.expression()

        return ReturnNode(
            value,
            command.line,
            command.column,
        )

    def break_statement(self):
        command = self.previous()

        self.consume_statement_boundary(
            command,
            "break",
        )

        return BreakNode(
            command.line,
            command.column,
        )

    def continue_statement(self):
        command = self.previous()

        self.consume_statement_boundary(
            command,
            "continue",
        )

        return ContinueNode(
            command.line,
            command.column,
        )

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

    def help_statement(self):
        command = self.consume(TokenType.IDENTIFIER)

        arguments = []

        if (
            self.check(TokenType.IDENTIFIER)
            and self.peek().line == command.line
        ):
            topic = self.advance()
            arguments.append(
                StringNode(
                    topic.value,
                    topic.line,
                    topic.column,
                )
            )
        elif (
            self.check(TokenType.STRING)
            and self.peek().line == command.line
        ):
            topic = self.advance()
            arguments.append(
                StringNode(
                    topic.value,
                    topic.line,
                    topic.column,
                )
            )
        elif (
            self.peek().line == command.line
            and not self.check(TokenType.SEMICOLON)
            and not self.is_at_end()
        ):
            token = self.peek()

            raise ParserError(
                "Expected help topic",
                line=token.line,
                column=token.column,
                token=token.value,
            )

        return FunctionCallNode(
            "help",
            arguments,
            command.line,
            command.column,
        )

    def lookfor_statement(self):
        command = self.consume(TokenType.IDENTIFIER)

        arguments = []

        if (
            self.check(TokenType.IDENTIFIER)
            and self.peek().line == command.line
        ):
            topic = self.advance()
            arguments.append(
                StringNode(
                    topic.value,
                    topic.line,
                    topic.column,
                )
            )
        elif (
            self.check(TokenType.STRING)
            and self.peek().line == command.line
        ):
            topic = self.advance()
            arguments.append(
                StringNode(
                    topic.value,
                    topic.line,
                    topic.column,
                )
            )
        else:
            token = self.peek()

            raise ParserError(
                "Expected lookfor keyword",
                line=token.line,
                column=token.column,
                token=token.value,
            )

        return FunctionCallNode(
            "lookfor",
            arguments,
            command.line,
            command.column,
        )

    def cwd_statement(self):
        command = self.consume(TokenType.IDENTIFIER)

        return FunctionCallNode(
            "cwd",
            [],
            command.line,
            command.column,
        )

    def who_statement(self):
        command = self.consume(TokenType.IDENTIFIER)

        return FunctionCallNode(
            "who",
            [],
            command.line,
            command.column,
        )

    def figure_statement(self):
        command = self.consume(TokenType.IDENTIFIER)

        return FunctionCallNode(
            "figure",
            [],
            command.line,
            command.column,
        )

    def close_statement(self):
        command = self.consume(TokenType.IDENTIFIER)
        arguments = []

        if (
            self.check(TokenType.IDENTIFIER)
            and self.peek().line == command.line
            and self.peek().value == "all"
        ):
            argument = self.advance()
            arguments.append(
                StringNode(
                    "all",
                    argument.line,
                    argument.column,
                )
            )

        return FunctionCallNode(
            "close",
            arguments,
            command.line,
            command.column,
        )
    
    def function_declaration(self):
        return_variable = None
        return_variables = []

        # Optional return variable(s)
        if self.match(TokenType.LBRACKET):
            return_variables = self.function_return_list()
            return_variable = (
                return_variables[0]
                if return_variables
                else None
            )

            self.consume(TokenType.EQUAL)

            function_name = self.consume(
                TokenType.IDENTIFIER
            )

        elif self.check(TokenType.IDENTIFIER):
            identifier = self.advance()

            if self.match(TokenType.EQUAL):
                return_variable = identifier.value
                return_variables = [return_variable]

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
            return_variable,
            return_variables
        )

    def function_return_list(self):
        return_variables = []

        if self.check(TokenType.RBRACKET):
            raise ParserError(
                "Expected function return variable",
                line=self.peek().line,
                column=self.peek().column,
                token=self.peek().value,
            )

        identifier = self.consume(TokenType.IDENTIFIER)
        return_variables.append(identifier.value)

        while not self.check(TokenType.RBRACKET):
            self.match(TokenType.COMMA)

            identifier = self.consume(TokenType.IDENTIFIER)
            return_variables.append(identifier.value)

        self.consume(TokenType.RBRACKET)

        return return_variables

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
        node = self.unary()

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
        node = self.postfix()

        if self.match(
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

        while True:
            if self.match(TokenType.LPAREN):
                paren = self.previous()
                arguments = self.function_arguments()

                self.consume(TokenType.RPAREN)

                if isinstance(expr, IdentifierNode):
                    expr = FunctionCallNode(
                        expr.name,
                        arguments,
                        expr.line,
                        expr.column,
                    )
                else:
                    expr = IndexAccessNode(
                        expr,
                        arguments,
                        paren.line,
                        paren.column,
                    )

                continue

            if self.match(TokenType.DOT):
                dot = self.previous()
                field = self.consume(TokenType.IDENTIFIER)

                expr = FieldAccessNode(
                    expr,
                    field.value,
                    dot.line,
                    dot.column,
                )

                continue

            if self.match(TokenType.TRANSPOSE):
                operator = self.previous()
                expr = TransposeNode(
                    expr,
                    operator.line,
                    operator.column,
                )

                continue

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

        return self.power()

    def primary(self):
        if self.match(TokenType.STRING):
            token = self.previous()

            return StringNode(token.value, token.line, token.column)
        
        if self.match(TokenType.NUMBER):
            token = self.previous()

            return NumberNode(token.value,token.line, token.column )
        
        if self.match(TokenType.TRUE):
            token = self.previous()

            if self.match(TokenType.LPAREN):
                arguments = self.function_arguments()

                self.consume(TokenType.RPAREN)

                return FunctionCallNode(
                    "true",
                    arguments,
                    token.line,
                    token.column,
                )

            return NumberNode(True, token.line, token.column)

        if self.match(TokenType.FALSE):
            token = self.previous()

            if self.match(TokenType.LPAREN):
                arguments = self.function_arguments()

                self.consume(TokenType.RPAREN)

                return FunctionCallNode(
                    "false",
                    arguments,
                    token.line,
                    token.column,
                )

            return NumberNode(False, token.line, token.column)

        if self.match(TokenType.IDENTIFIER):
            identifier = self.previous()

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

    def function_arguments(self):
        arguments = []

        if self.check(TokenType.RPAREN):
            return arguments

        arguments.append(
            self.function_argument()
        )

        while self.match(TokenType.COMMA):
            arguments.append(
                self.function_argument()
            )

        return arguments

    def function_argument(self):
        if (
            self.check(TokenType.IDENTIFIER)
            and self.peek_next().type == TokenType.EQUAL
        ):
            name = self.advance()
            self.consume(TokenType.EQUAL)
            value = self.expression()

            return NameValueNode(
                name.value,
                value,
                name.line,
                name.column
            )

        return self.expression()
    
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

            if self.matrix_element_uses_full_expression():
                value = self.expression()
            else:
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
                TokenType.TRUE,
                TokenType.FALSE,
                TokenType.MINUS,
                TokenType.STRING,
                TokenType.LPAREN,
            ):
                continue

            raise ParserError(
                "Expected matrix separator or closing bracket",
                line=next_token.line,
                column=next_token.column,
                token=next_token.value,
            )

        if current_row:
            rows.append(current_row)

        self.consume(TokenType.RBRACKET)

        token = self.previous()

        return MatrixNode(rows, token.line, token.column)    
    
    def matrix_expression(self):
        start = self.matrix_atom()

        if (
            self.check(TokenType.PLUS)
            or self.check(TokenType.MINUS)
        ):
            operator = self.peek()

            if self.is_imaginary_literal(
                self.peek_next()
            ):
                self.advance()
                right = self.matrix_atom()

                return BinaryOpNode(
                    start,
                    operator.type,
                    right,
                    operator.line,
                    operator.column
                )

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

    def matrix_atom(self):
        if self.match(TokenType.MINUS):
            operand = self.power()

            return UnaryOpNode(
                TokenType.MINUS,
                operand
            )

        return self.power()

    def is_imaginary_literal(self, token):
        return (
            token.type == TokenType.NUMBER
            and isinstance(token.value, complex)
            and token.value.real == 0
        )

    def matrix_element_uses_full_expression(self):
        depth = 0
        position = self.position

        while position < len(self.tokens):
            token_type = self.tokens[position].type

            if token_type in (
                TokenType.LPAREN,
                TokenType.LBRACKET,
            ):
                depth += 1

            elif token_type in (
                TokenType.RPAREN,
                TokenType.RBRACKET,
            ):
                if depth == 0:
                    return False

                depth -= 1

            elif (
                depth == 0
                and token_type in (
                    TokenType.COMMA,
                    TokenType.SEMICOLON,
                    TokenType.RBRACKET,
                )
            ):
                return False

            elif (
                depth == 0
                and token_type == TokenType.EQEQ
            ):
                return True

            position += 1

        return False

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
        if self.peek().type == TokenType.LBRACKET:
            return self.is_multi_assignment_start()

        if self.peek().type != TokenType.IDENTIFIER:
            return False

        depth = 0
        start_line = self.peek().line
        position = self.position

        while position < len(self.tokens):
            current = self.tokens[position]
            token_type = current.type

            if current.line != start_line:
                return False

            if token_type == TokenType.LPAREN:
                depth += 1
            elif token_type == TokenType.RPAREN:
                depth = max(depth - 1, 0)
            elif depth == 0 and token_type == TokenType.EQUAL:
                return True
            elif (
                depth == 0
                and token_type in (
                    TokenType.SEMICOLON,
                    TokenType.EOF,
                )
            ):
                return False

            position += 1

        return False

    def is_multi_assignment_start(self):
        depth = 0
        position = self.position

        while position < len(self.tokens):
            token_type = self.tokens[position].type

            if token_type == TokenType.LBRACKET:
                depth += 1
            elif token_type == TokenType.RBRACKET:
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

    def is_help_statement(self):
        return (
            self.peek().type == TokenType.IDENTIFIER
            and self.peek().value == "help"
            and self.peek_next().type != TokenType.LPAREN
            and self.peek_next().type != TokenType.EQUAL
        )

    def is_lookfor_statement(self):
        return (
            self.peek().type == TokenType.IDENTIFIER
            and self.peek().value == "lookfor"
            and self.peek_next().type != TokenType.LPAREN
            and self.peek_next().type != TokenType.EQUAL
        )

    def is_cwd_statement(self):
        next_token = self.peek_next()

        return (
            self.peek().type == TokenType.IDENTIFIER
            and self.peek().value == "cwd"
            and next_token.type != TokenType.LPAREN
            and next_token.type != TokenType.EQUAL
            and (
                next_token.type == TokenType.SEMICOLON
                or next_token.type == TokenType.EOF
                or next_token.line != self.peek().line
            )
        )

    def is_who_statement(self):
        next_token = self.peek_next()

        return (
            self.peek().type == TokenType.IDENTIFIER
            and self.peek().value == "who"
            and next_token.type != TokenType.LPAREN
            and next_token.type != TokenType.EQUAL
            and (
                next_token.type == TokenType.SEMICOLON
                or next_token.type == TokenType.EOF
                or next_token.line != self.peek().line
            )
        )

    def is_figure_statement(self):
        next_token = self.peek_next()

        return (
            self.peek().type == TokenType.IDENTIFIER
            and self.peek().value == "figure"
            and next_token.type != TokenType.LPAREN
            and next_token.type != TokenType.EQUAL
            and (
                next_token.type == TokenType.SEMICOLON
                or next_token.type == TokenType.EOF
                or next_token.line != self.peek().line
            )
        )

    def is_close_statement(self):
        next_token = self.peek_next()

        if (
            self.peek().type != TokenType.IDENTIFIER
            or self.peek().value != "close"
            or next_token.type == TokenType.LPAREN
            or next_token.type == TokenType.EQUAL
        ):
            return False

        if (
            next_token.type == TokenType.SEMICOLON
            or next_token.type == TokenType.EOF
            or next_token.line != self.peek().line
        ):
            return True

        after_argument = self.peek_at(2)

        return (
            next_token.type == TokenType.IDENTIFIER
            and next_token.value == "all"
            and (
                after_argument.type == TokenType.SEMICOLON
                or after_argument.type == TokenType.EOF
                or after_argument.line != self.peek().line
            )
        )

    def is_statement_boundary(self, line):
        return (
            self.is_at_end()
            or self.check(TokenType.SEMICOLON)
            or self.check(TokenType.END)
            or self.check(TokenType.ELSE)
            or self.check(TokenType.ELSEIF)
            or self.peek().line != line
        )

    def consume_statement_boundary(self, command, keyword):
        if self.is_statement_boundary(command.line):
            return

        token = self.peek()

        raise ParserError(
            f"Unexpected token after '{keyword}'",
            line=token.line,
            column=token.column,
            token=token.value,
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

    def peek_at(self, offset):
        position = self.position + offset

        if position >= len(self.tokens):
            return self.tokens[-1]

        return self.tokens[position]

    def previous(self):
        return self.tokens[self.position - 1]
