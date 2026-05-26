from gui.main_window import MainWindow


class FakeDocument:
    def __init__(self, modified=False):
        self.modified = modified

    def isModified(self):
        return self.modified

    def setModified(self, modified):
        self.modified = modified


class FakeEditor:
    def __init__(
        self,
        text="",
        file_path=None,
        modified=False,
    ):
        self.text = text
        self.file_path = file_path
        self._document = FakeDocument(modified)

    def document(self):
        return self._document

    def toPlainText(self):
        return self.text


class FakeTabs:
    def __init__(self, editors=None, titles=None):
        self.editors = list(editors or [])
        self.titles = list(
            titles
            or ["Untitled" for _ in self.editors]
        )
        self.tooltips = [
            "" for _ in self.editors
        ]
        self.current_index = 0 if self.editors else -1

    def count(self):
        return len(self.editors)

    def widget(self, index):
        return self.editors[index]

    def currentWidget(self):
        if self.current_index == -1:
            return None

        return self.editors[self.current_index]

    def currentIndex(self):
        return self.current_index

    def indexOf(self, editor):
        try:
            return self.editors.index(editor)
        except ValueError:
            return -1

    def tabText(self, index):
        return self.titles[index]

    def setTabText(self, index, title):
        self.titles[index] = title

    def setTabToolTip(self, index, tooltip):
        self.tooltips[index] = tooltip

    def setCurrentWidget(self, editor):
        self.current_index = self.indexOf(editor)

    def setCurrentIndex(self, index):
        self.current_index = index

    def removeTab(self, index):
        del self.editors[index]
        del self.titles[index]
        del self.tooltips[index]

        if not self.editors:
            self.current_index = -1
        else:
            self.current_index = min(
                index,
                len(self.editors) - 1,
            )

    def add_editor(self, editor, title):
        self.editors.append(editor)
        self.titles.append(title)
        self.tooltips.append("")
        self.current_index = len(self.editors) - 1


class DummyConsole:
    def __init__(self):
        self.messages = []

    def appendPlainText(self, message):
        self.messages.append(message)


class WindowHarness:
    close_tab = MainWindow.close_tab
    confirm_close_editors = MainWindow.confirm_close_editors
    editor_display_name = MainWindow.editor_display_name
    set_editor_tab_title = MainWindow.set_editor_tab_title
    save_editor = MainWindow.save_editor


def make_window(editor, title="Untitled"):
    window = WindowHarness()
    window.tabs = FakeTabs([editor], [title])
    window.console = DummyConsole()
    return window


def test_close_tab_discard_closes_last_script_and_opens_clean_tab():
    editor = FakeEditor("x = 1", modified=True)
    window = make_window(editor, "Untitled*")
    window.prompt_unsaved_changes = (
        lambda editors, action: "discard"
    )
    window.create_new_tab = lambda: window.tabs.add_editor(
        FakeEditor(),
        "Untitled",
    )

    window.close_tab(0)

    assert window.tabs.count() == 1
    assert window.tabs.widget(0) is not editor
    assert window.tabs.tabText(0) == "Untitled"


def test_close_tab_cancel_keeps_unsaved_script_open():
    editor = FakeEditor("x = 1", modified=True)
    window = make_window(editor, "Untitled*")
    window.prompt_unsaved_changes = (
        lambda editors, action: "cancel"
    )

    window.close_tab(0)

    assert window.tabs.count() == 1
    assert window.tabs.widget(0) is editor


def test_confirm_quit_save_saves_each_dirty_script():
    first = FakeEditor("a = 1", modified=True)
    second = FakeEditor("b = 2", modified=True)
    window = WindowHarness()
    window.tabs = FakeTabs(
        [first, second],
        ["first.m*", "second.m*"],
    )
    window.prompt_unsaved_changes = (
        lambda editors, action: "save"
    )

    saved = []
    window.save_editor = (
        lambda editor: saved.append(editor) or True
    )

    assert window.confirm_close_editors(
        [first, second],
        "quit",
    )
    assert saved == [first, second]


def test_save_editor_writes_file_and_clears_dirty_marker(tmp_path):
    path = tmp_path / "script.m"
    editor = FakeEditor(
        "answer = 42",
        file_path=str(path),
        modified=True,
    )
    window = make_window(editor, "script.m*")

    assert window.save_editor(editor)

    assert path.read_text(encoding="utf-8") == "answer = 42"
    assert not editor.document().isModified()
    assert window.tabs.tabText(0) == "script.m"
    assert window.tabs.tooltips[0] == str(path)
