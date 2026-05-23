from core.engine import MathToolSession
from core.plotting.recording import RecordingPlotEngine
from core.runtime.context import RuntimeContext


def test_session_executes_source_and_keeps_workspace_between_calls():
    session = MathToolSession()

    first = session.execute("A = 1 + 2;")
    second = session.execute("B = A + 4;")

    assert first.value == 3
    assert second.value == 7
    assert session.context.variables["A"] == 3
    assert session.context.variables["B"] == 7


def test_session_routes_output_and_restores_existing_callback():
    context = RuntimeContext()
    original_output = []
    original_callback = original_output.append
    context.output_callback = original_callback

    session = MathToolSession(context=context)
    routed_output = []

    result = session.execute(
        'disp("hello");',
        output_callback=routed_output.append,
    )

    assert result.output == ["hello\n"]
    assert routed_output == ["hello\n"]
    assert original_output == []
    assert context.output_callback is original_callback


def test_session_runs_bare_script_command_when_enabled(tmp_path):
    script = tmp_path / "script_1.m"
    script.write_text(
        "value = 4 + 1;\n",
        encoding="utf-8",
    )

    session = MathToolSession()
    session.context.set_current_working_directory(
        tmp_path
    )

    result = session.execute(
        "script_1",
        allow_script_commands=True,
    )

    assert result.value == 5
    assert result.source_path == str(script.resolve())
    assert session.context.variables["value"] == 5


def test_session_handles_interactive_workspace_commands():
    session = MathToolSession()
    session.execute("A = 10;")

    who = session.execute(
        "who",
        allow_commands=True,
    )
    cleared = session.execute(
        "clear",
        allow_commands=True,
    )

    assert who.value == ["A"]
    assert cleared.value == "Workspace cleared"
    assert "A" not in session.context.variables


def test_session_handles_doc_command_and_semicolon_help_topic():
    session = MathToolSession()

    help_result = session.execute(
        "help plot;",
        allow_commands=True,
    )
    doc_result = session.execute(
        "doc plotting-guide",
        allow_commands=True,
    )

    assert help_result.command == "help"
    assert help_result.help_topic == "plot"
    assert "Plot x-y data" in help_result.value

    assert doc_result.command == "doc"
    assert doc_result.help_topic == "plotting-guide"
    assert "Plotting Guide" in doc_result.value


def test_session_executes_figure_and_close_commands():
    plot_engine = RecordingPlotEngine()
    session = MathToolSession(
        plot_engine=plot_engine
    )

    session.execute(
        """
figure
plot([1 2], [3 4]);
figure(2);
plot([5 6], [7 8]);
close(1);
"""
    )

    assert [
        plot["id"]
        for plot in plot_engine.serialize_plots()
    ] == [2]

    session.execute("close all")

    assert plot_engine.serialize_plots() == []


def test_session_executes_bode_and_nyquist_plots():
    plot_engine = RecordingPlotEngine()
    session = MathToolSession(
        plot_engine=plot_engine
    )

    session.execute(
        """
w = [0.1 1 10];
bode([1], [1 1], w);
nyquist([1], [1 1], [0 1]);
"""
    )

    plots = plot_engine.serialize_plots()

    assert len(plots) == 3
    assert plots[0]["layout"]["title"]["text"] == (
        "Bode Diagram - Magnitude"
    )
    assert plots[0]["layout"]["xaxis"]["type"] == "log"
    assert plots[2]["layout"]["title"]["text"] == "Nyquist Diagram"
