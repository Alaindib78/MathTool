from gui.main_window import MainWindow
from gui.main_window import QFileDialog

from core.runtime.context import RuntimeContext


class PathWindowHarness:
    search_path_directories = (
        MainWindow.search_path_directories
    )
    add_search_path = MainWindow.add_search_path
    include_subdirectories_for_path_add = (
        MainWindow.include_subdirectories_for_path_add
    )


class ReplWindowHarness:
    execute_repl_code = MainWindow.execute_repl_code


class DummyConsole:
    def __init__(self):
        self.messages = []

    def appendPlainText(self, message):
        self.messages.append(message)


def make_path_window():
    window = PathWindowHarness()
    window.context = RuntimeContext()
    window.console = DummyConsole()
    window.include_subdirectories_on_add = True
    window.save_runtime_settings = lambda: None
    window.update_runtime_path_ui = lambda: None
    return window


def normalized_paths(window, *paths):
    return [
        window.context.normalize_directory(path)
        for path in paths
    ]


def test_gui_repl_who_returns_workspace_names():
    window = ReplWindowHarness()
    window.execution_thread = None
    window.context = RuntimeContext()
    window.context.set_variable("alpha", 1)

    assert window.execute_repl_code("who") == ["alpha"]


def test_search_path_directories_can_include_subdirectories(tmp_path):
    root = tmp_path / "library"
    alpha = root / "alpha"
    nested = alpha / "nested"
    beta = root / "beta"

    nested.mkdir(parents=True)
    beta.mkdir(parents=True)

    window = make_path_window()

    assert window.search_path_directories(
        root,
        include_subdirectories=True,
    ) == normalized_paths(
        window,
        root,
        alpha,
        nested,
        beta,
    )


def test_search_path_directories_can_skip_subdirectories(tmp_path):
    root = tmp_path / "library"
    child = root / "child"

    child.mkdir(parents=True)

    window = make_path_window()

    assert window.search_path_directories(
        root,
        include_subdirectories=False,
    ) == normalized_paths(
        window,
        root,
    )


def test_add_search_path_uses_dialog_when_qt_sends_checked_argument(
    tmp_path,
    monkeypatch,
):
    root = tmp_path / "library"
    child = root / "child"

    child.mkdir(parents=True)

    window = make_path_window()

    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        lambda *args: str(root),
    )

    window.add_search_path(False)

    assert window.context.search_paths == normalized_paths(
        window,
        root,
        child,
    )
