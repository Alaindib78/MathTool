import math

import pytest

from core.runtime.context import RuntimeContext


def test_runtime_context_loads_constants_and_hides_them_from_who():
    context = RuntimeContext()
    context.set_variable("answer", 42)

    assert context.variables["pi"] == math.pi
    assert context.variables["e"] == math.e
    assert context.variables["true"] is True
    assert context.variables["false"] is False
    assert context.who() == ["answer"]


def test_runtime_context_clear_preserves_constants_only():
    context = RuntimeContext()
    context.set_variable("scratch", 123)

    context.clear()

    assert "scratch" not in context.variables
    assert context.variables["pi"] == math.pi
    assert context.variables["e"] == math.e


def test_child_context_shares_functions_but_not_parent_variables():
    context = RuntimeContext()
    marker = object()
    context.functions.register("custom", marker)
    context.set_variable("parent_only", 1)

    child = context.create_child_context()

    assert child.functions.get("custom") is marker
    with pytest.raises(Exception, match="Undefined variable 'parent_only'"):
        child.get_variable("parent_only")
