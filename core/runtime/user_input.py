import builtins

import numpy as np

from core.errors.errors import RuntimeError as MathToolRuntimeError


def request_user_input(context, prompt, mode=None):
    if not isinstance(prompt, str):
        raise MathToolRuntimeError(
            "input: prompt must be a string"
        )

    raw_text = _read_text(context, prompt)

    if mode is None:
        return _evaluate_response(context, raw_text, prompt)

    if isinstance(mode, str) and mode.lower() == "s":
        return raw_text

    raise MathToolRuntimeError(
        "input: second argument must be 's'"
    )


def _read_text(context, prompt):
    callback = getattr(context, "input_callback", None)

    if callback is not None:
        return str(callback(prompt))

    return builtins.input(prompt)


def _evaluate_response(context, raw_text, prompt):
    if raw_text == "":
        return np.array([])

    while True:
        try:
            return _evaluate_expression(context, raw_text)
        except Exception as error:
            if context.output_callback is not None:
                context.output_callback(str(error) + "\n")

            raw_text = _read_text(context, prompt)

            if raw_text == "":
                return np.array([])


def _evaluate_expression(context, source):
    from core.interpreter.interpreter import Interpreter
    from core.lexer.lexer import Lexer
    from core.parser.parser import Parser

    program = Parser(
        Lexer(source).tokenize()
    ).parse()

    previous_output_callback = context.output_callback
    context.output_callback = None

    try:
        return Interpreter(context).evaluate(program)
    finally:
        context.output_callback = previous_output_callback
