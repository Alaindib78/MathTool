import os

os.environ.setdefault(
    "QT_QPA_PLATFORM",
    "offscreen",
)

import pytest
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication

from core.runtime.context import RuntimeContext
from gui.documentation_panel import DocumentationPanel


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_documentation_panel_searches_and_renders_user_help(
    tmp_path,
    app,
):
    (tmp_path / "squareNumber.m").write_text(
        """
function y = squareNumber(x)
% SQUARENUMBER Squares the input value.
%
%   See also sqrt
    y = x ^ 2;
end
""",
        encoding="utf-8",
    )

    context = RuntimeContext()
    context.set_current_working_directory(tmp_path)

    panel = DocumentationPanel(context.help_database)

    panel.search_edit.setText("square")

    assert panel.result_list.count() >= 1
    assert any(
        "squareNumber" in panel.result_list.item(row).text()
        for row in range(panel.result_list.count())
    )
    assert "function y = squareNumber(x)" in panel.signature_label.text()
    assert "SQUARENUMBER Squares" in panel.browser.toPlainText()

    panel.open_topic("sqrt")

    assert "sqrt" in panel.signature_label.text()


def test_documentation_panel_navigates_topic_links(app):
    context = RuntimeContext()
    panel = DocumentationPanel(context.help_database)

    panel.on_anchor_clicked(QUrl("topic:plotting-guide"))

    assert panel.current_topic == "plotting-guide"
    assert "Plotting Guide" in panel.browser.toPlainText()

    panel.on_anchor_clicked(QUrl("category:Plotting"))

    assert "Plotting" in panel.search_edit.text()
