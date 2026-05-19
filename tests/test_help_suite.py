from core.stdlib.builtins import BUILTIN_FUNCTIONS
from core.stdlib.help_text import HELP_TOPICS, format_help


def test_every_builtin_has_help_text():
    missing = set(BUILTIN_FUNCTIONS) - set(HELP_TOPICS)

    assert missing == set()


def test_help_text_has_required_sections_for_every_builtin():
    for name in BUILTIN_FUNCTIONS:
        text = format_help(name)

        assert f"{name}\n" in text
        assert "Definition:" in text
        assert "Syntax:" in text
        assert "Inputs:" in text
        assert "Output:" in text
        assert "Options:" in text


def test_help_overview_lists_available_topics():
    text = format_help()

    assert "MathTool help" in text
    assert "Available topics:" in text
    assert "eig" in text
    assert "linspace" in text
