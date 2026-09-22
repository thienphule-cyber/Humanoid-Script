"""
parser.py

Phase 2/3 — Parser.

Recursive-descent parser that converts a list of Tokens
(from the Lexer) into an AST (Program node).
"""

from humanoidscript.lexer.tokens import Token, TokenType
from humanoidscript.parser.ast import (
    Program,
    NumberLiteral,
    StringLiteral,
    BooleanLiteral,
    Identifier,
    BinaryOp,
    FunctionCall,
    VariableDeclaration,
    PrintStatement,
    RobotDeclaration,
    ObjectDeclaration,
    IfStatement,
    WhileStatement,
    FunctionDeclaration,
    ReturnStatement,
    WalkCommand,
    TurnCommand,
    StandCommand,
    ReachCommand,
    GraspCommand,
    ReleaseCommand,
)

DIRECTIONS = {"forward", "backward", "left", "right"}
COMPARISON_OPS = {"==", "!=", "<", ">", "<=", ">="}


class ParseError(Exception):
    """Raised when the parser encounters invalid syntax."""
    pass


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    # -----------------------------------------------------------
    # Entry point
    # -----------------------------------------------------------
    def parse(self) -> Program:
        statements = self._parse_block(stop_keywords=set())
        return Program(statements=statements)

    # -----------------------------------------------------------
    # Block parsing (used by program body, if/while/function bodies)
    # -----------------------------------------------------------
    def _parse_block(self, stop_keywords: set) -> list:
        statements = []
        self._skip_newlines()

        while not self._check(TokenType.EOF):
            token = self._peek()
            if token.type == TokenType.KEYWORD and token.value in stop_keywords:
                break
            statements.append(self._parse_statement())
            self._skip_newlines()

        return statements

    # -----------------------------------------------------------
    # Statements
    # -----------------------------------------------------------
    def _parse_statement(self):
        token = self._peek()

        if token.type == TokenType.KEYWORD:
            keyword = token.value

            if keyword == "let":
                return self._parse_variable_declaration()
            if keyword == "print":
                return self._parse_print_statement()
            if keyword == "robot":
                return self._parse_robot_declaration()
            if keyword == "object":
                return self._parse_object_declaration()
            if keyword == "walk":
                return self._parse_walk_command()
            if keyword == "turn":
                return self._parse_turn_command()
            if keyword == "stand":
                self._advance()
                return StandCommand()
            if keyword == "reach":
                return self._parse_reach_command()
            if keyword == "grasp":
                return self._parse_grasp_command()
            if keyword == "release":
                return self._parse_release_command()
            if keyword == "if":
                return self._parse_if_statement()
            if keyword == "while":
                return self._parse_while_statement()
            if keyword == "function":
                return self._parse_function_declaration()
            if keyword == "return":
                return self._parse_return_statement()

        # Bare function call used as a statement, e.g. `greet("Kelvin")`
        if token.type == TokenType.IDENTIFIER:
            return self._parse_expression_statement()

        raise ParseError(
            f"Line {token.line}: Unexpected token {token.value!r}"
        )

    def _parse_variable_declaration(self) -> VariableDeclaration:
        self._expect_keyword("let")
        name_token = self._expect(TokenType.IDENTIFIER)
        self._expect_operator("=")
        value = self._parse_expression()
        return VariableDeclaration(name=name_token.value, value=value)

    def _parse_print_statement(self) -> PrintStatement:
        self._expect_keyword("print")
        self._expect(TokenType.LPAREN)
        expr = self._parse_expression()
        self._expect(TokenType.RPAREN)
        return PrintStatement(expression=expr)

    def _parse_robot_declaration(self) -> RobotDeclaration:
        self._expect_keyword("robot")
        name_token = self._expect(TokenType.IDENTIFIER)
        return RobotDeclaration(name=name_token.value)
    
    def _parse_object_declaration(self) -> ObjectDeclaration:
        self._expect_keyword("object")
        name_token = self._expect(TokenType.IDENTIFIER)
        self._expect_keyword_literal("at")
        self._expect(TokenType.LPAREN)
        x = self._parse_signed_number()
        self._expect(TokenType.COMMA)
        y = self._parse_signed_number()
        self._expect(TokenType.RPAREN)
        return ObjectDeclaration(name=name_token.value, x=x, y=y)

    def _parse_signed_number(self) -> float:
        sign = 1
        if self._check(TokenType.OPERATOR) and self._peek().value == "-":
            self._advance()
            sign = -1
        number_token = self._expect(TokenType.NUMBER)
        return sign * number_token.value

    def _parse_walk_command(self) -> WalkCommand:
        self._expect_keyword("walk")
        direction = self._expect_direction()
        number_token = self._expect(TokenType.NUMBER)
        unit_token = self._expect(TokenType.UNIT)
        return WalkCommand(
            direction=direction,
            distance=number_token.value,
            unit=unit_token.value,
        )

    def _parse_turn_command(self) -> TurnCommand:
        self._expect_keyword("turn")
        direction = self._expect_direction()
        number_token = self._expect(TokenType.NUMBER)
        unit_token = self._expect(TokenType.UNIT)
        return TurnCommand(
            direction=direction,
            angle=number_token.value,
            unit=unit_token.value,
        )

    def _parse_reach_command(self) -> ReachCommand:
        self._expect_keyword("reach")
        hand_token = self._expect(TokenType.IDENTIFIER)
        self._expect_keyword_literal("to")
        target_token = self._expect(TokenType.IDENTIFIER)
        return ReachCommand(hand=hand_token.value, target=target_token.value)

    def _parse_grasp_command(self) -> GraspCommand:
        self._expect_keyword("grasp")
        target_token = self._expect(TokenType.IDENTIFIER)
        return GraspCommand(target=target_token.value)

    def _parse_release_command(self) -> ReleaseCommand:
        self._expect_keyword("release")
        target_token = self._expect(TokenType.IDENTIFIER)
        return ReleaseCommand(target=target_token.value)
    
    def _parse_expression_statement(self):
        """
        Parses an expression used on its own as a statement.
        Currently only function calls make sense here
        (e.g. `greet("Kelvin")`), since a bare identifier or
        literal alone has no side effect.
        """
        expr = self._parse_expression()

        if not isinstance(expr, FunctionCall):
            token = self._peek()
            raise ParseError(
                f"Line {token.line}: Expression statement must be a function call"
            )

        return expr

    def _parse_if_statement(self) -> IfStatement:
        self._expect_keyword("if")
        condition = self._parse_expression()
        self._expect(TokenType.COLON)
        then_body = self._parse_block(stop_keywords={"else", "end"})

        else_body = None
        if self._check(TokenType.KEYWORD) and self._peek().value == "else":
            self._advance()
            self._expect(TokenType.COLON)
            else_body = self._parse_block(stop_keywords={"end"})

        self._expect_keyword("end")
        return IfStatement(condition=condition, then_body=then_body, else_body=else_body)

    def _parse_while_statement(self) -> WhileStatement:
        self._expect_keyword("while")
        condition = self._parse_expression()
        self._expect(TokenType.COLON)
        body = self._parse_block(stop_keywords={"end"})
        self._expect_keyword("end")
        return WhileStatement(condition=condition, body=body)

    def _parse_function_declaration(self) -> FunctionDeclaration:
        self._expect_keyword("function")
        name_token = self._expect(TokenType.IDENTIFIER)
        self._expect(TokenType.LPAREN)

        parameters = []
        if not self._check(TokenType.RPAREN):
            parameters.append(self._expect(TokenType.IDENTIFIER).value)
            while self._check(TokenType.COMMA):
                self._advance()
                parameters.append(self._expect(TokenType.IDENTIFIER).value)
        self._expect(TokenType.RPAREN)
        self._expect(TokenType.COLON)

        body = self._parse_block(stop_keywords={"end"})
        self._expect_keyword("end")

        return FunctionDeclaration(name=name_token.value, parameters=parameters, body=body)

    def _parse_return_statement(self) -> ReturnStatement:
        self._expect_keyword("return")

        if self._check(TokenType.NEWLINE) or self._check(TokenType.EOF):
            return ReturnStatement(expression=None)
        if self._check(TokenType.KEYWORD) and self._peek().value == "end":
            return ReturnStatement(expression=None)

        expr = self._parse_expression()
        return ReturnStatement(expression=expr)

    # -----------------------------------------------------------
    # Expressions (precedence climbing)
    # comparison -> additive -> multiplicative -> primary
    # -----------------------------------------------------------
    def _parse_expression(self):
        return self._parse_comparison()

    def _parse_comparison(self):
        left = self._parse_additive()

        while self._check(TokenType.OPERATOR) and self._peek().value in COMPARISON_OPS:
            op_token = self._advance()
            right = self._parse_additive()
            left = BinaryOp(left=left, operator=op_token.value, right=right)

        return left

    def _parse_additive(self):
        left = self._parse_multiplicative()

        while self._check(TokenType.OPERATOR) and self._peek().value in ("+", "-"):
            op_token = self._advance()
            right = self._parse_multiplicative()
            left = BinaryOp(left=left, operator=op_token.value, right=right)

        return left

    def _parse_multiplicative(self):
        left = self._parse_primary()

        while self._check(TokenType.OPERATOR) and self._peek().value in ("*", "/"):
            op_token = self._advance()
            right = self._parse_primary()
            left = BinaryOp(left=left, operator=op_token.value, right=right)

        return left

    def _parse_primary(self):
        token = self._peek()

        if token.type == TokenType.NUMBER:
            self._advance()
            unit = None
            if self._check(TokenType.UNIT):
                unit = self._advance().value
            return NumberLiteral(value=token.value, unit=unit)

        if token.type == TokenType.STRING:
            self._advance()
            return StringLiteral(value=token.value)

        if token.type == TokenType.KEYWORD and token.value in ("true", "false"):
            self._advance()
            return BooleanLiteral(value=(token.value == "true"))

        if token.type == TokenType.IDENTIFIER:
            self._advance()
            if self._check(TokenType.LPAREN):
                return self._parse_call(token.value)
            return Identifier(name=token.value)

        if token.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN)
            return expr

        raise ParseError(f"Line {token.line}: Expected expression, got {token.value!r}")

    def _parse_call(self, name: str) -> FunctionCall:
        self._expect(TokenType.LPAREN)
        args = []
        if not self._check(TokenType.RPAREN):
            args.append(self._parse_expression())
            while self._check(TokenType.COMMA):
                self._advance()
                args.append(self._parse_expression())
        self._expect(TokenType.RPAREN)
        return FunctionCall(name=name, arguments=args)

    # -----------------------------------------------------------
    # Token stream helpers
    # -----------------------------------------------------------
    def _peek(self) -> Token:
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        token = self.tokens[self.pos]
        if token.type != TokenType.EOF:
            self.pos += 1
        return token

    def _check(self, token_type: TokenType) -> bool:
        return self._peek().type == token_type

    def _skip_newlines(self) -> None:
        while self._check(TokenType.NEWLINE):
            self._advance()

    def _expect(self, token_type: TokenType) -> Token:
        token = self._peek()
        if token.type != token_type:
            raise ParseError(
                f"Line {token.line}: Expected {token_type.name}, "
                f"got {token.type.name} ({token.value!r})"
            )
        return self._advance()

    def _expect_keyword(self, keyword: str) -> Token:
        token = self._peek()
        if token.type != TokenType.KEYWORD or token.value != keyword:
            raise ParseError(
                f"Line {token.line}: Expected keyword {keyword!r}, got {token.value!r}"
            )
        return self._advance()

    def _expect_keyword_literal(self, keyword: str) -> Token:
        token = self._peek()
        if token.value != keyword:
            raise ParseError(
                f"Line {token.line}: Expected {keyword!r}, got {token.value!r}"
            )
        return self._advance()

    def _expect_operator(self, operator: str) -> Token:
        token = self._peek()
        if token.type != TokenType.OPERATOR or token.value != operator:
            raise ParseError(
                f"Line {token.line}: Expected operator {operator!r}, got {token.value!r}"
            )
        return self._advance()

    def _expect_direction(self) -> str:
        token = self._peek()
        if token.type != TokenType.KEYWORD or token.value not in DIRECTIONS:
            raise ParseError(
                f"Line {token.line}: Expected a direction "
                f"(forward/backward/left/right), got {token.value!r}"
            )
        self._advance()
        return token.value


def parse(source_tokens: list[Token]) -> Program:
    """Convenience function: parse a token list into a Program AST."""
    return Parser(source_tokens).parse()