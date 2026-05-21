import math

import pytest
from pathlib import Path

from core.runtime.context import (
    DEFAULT_LIBRARY_DIRECTORY,
    RuntimeContext,
)


def test_runtime_context_loads_constants_and_hides_them_from_who():
    context = RuntimeContext()
    context.set_variable("answer", 42)

    assert context.variables["pi"] == math.pi
    assert context.variables["e"] == math.e
    assert context.variables["true"] is True
    assert context.variables["false"] is False
    assert context.get_variable("i") == 1j
    assert context.get_variable("j") == 1j
    assert context.who() == ["answer"]


def test_runtime_context_clear_preserves_constants_only():
    context = RuntimeContext()
    context.set_variable("scratch", 123)
    context.set_variable("i", 5)

    context.clear()

    assert "scratch" not in context.variables
    assert "i" not in context.variables
    assert context.variables["pi"] == math.pi
    assert context.variables["e"] == math.e
    assert context.get_variable("i") == 1j


def test_child_context_shares_functions_but_not_parent_variables():
    context = RuntimeContext()
    marker = object()
    context.functions.register("custom", marker)
    context.set_variable("parent_only", 1)

    child = context.create_child_context()

    assert child.functions.get("custom") is marker
    with pytest.raises(Exception, match="Undefined variable 'parent_only'"):
        child.get_variable("parent_only")


def test_runtime_context_notifies_when_paths_change(tmp_path):
    context = RuntimeContext()
    notifications = []

    context.path_changed_callback = (
        lambda: notifications.append(True)
    )

    context.set_current_working_directory(tmp_path)

    assert context.current_working_directory == str(
        tmp_path.resolve()
    )
    assert notifications == [True]


def test_runtime_context_registers_default_core_library_path():
    context = RuntimeContext()

    assert context.library_paths[0] == str(
        DEFAULT_LIBRARY_DIRECTORY.resolve()
    )
    assert all(
        DEFAULT_LIBRARY_DIRECTORY.resolve()
        in Path(path).resolve().parents
        or Path(path).resolve()
        == DEFAULT_LIBRARY_DIRECTORY.resolve()
        for path in context.library_paths
    )
