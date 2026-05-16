from core.interpreter.interpreter import Interpreter
from core.runtime.context import RuntimeContext
from core.semantic.semantic_analyzer import SemanticAnalyzer
from gui.execution_worker import ExecutionWorker


def test_execution_worker_routes_output_through_signal_and_restores_callback():
    context = RuntimeContext()
    original_output = []
    original_callback = original_output.append
    context.output_callback = original_callback

    worker = ExecutionWorker(
        'print("hello");\nA = 1 + 2;',
        SemanticAnalyzer(),
        Interpreter(context),
    )
    output = []
    finished = []
    errors = []
    workspace_updates = []

    worker.output.connect(output.append)
    worker.finished.connect(finished.append)
    worker.error.connect(errors.append)
    worker.workspace_updated.connect(
        lambda: workspace_updates.append(True)
    )

    worker.run()

    assert output == ["hello"]
    assert original_output == []
    assert finished == [3.0]
    assert errors == []
    assert workspace_updates == [True]
    assert context.variables["A"] == 3.0
    assert context.output_callback is original_callback


def test_execution_worker_emits_errors_and_restores_callback():
    context = RuntimeContext()
    original_callback = lambda text: None
    context.output_callback = original_callback

    worker = ExecutionWorker(
        "A = 5 / 0;",
        SemanticAnalyzer(),
        Interpreter(context),
    )
    finished = []
    errors = []

    worker.finished.connect(finished.append)
    worker.error.connect(errors.append)

    worker.run()

    assert finished == []
    assert len(errors) == 1
    assert "Division by zero" in errors[0]
    assert context.output_callback is original_callback
