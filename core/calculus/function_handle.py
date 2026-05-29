class FunctionHandle:
    def __init__(
        self,
        parameters,
        body,
        closure_context,
    ):
        self.parameters = list(parameters)
        self.body = body
        self.closure_context = closure_context
        self.closure_variables = dict(
            closure_context.variables
        )

    def __call__(self, *arguments):
        if len(arguments) != len(self.parameters):
            raise Exception(
                "function handle expected "
                f"{len(self.parameters)} argument(s), "
                f"got {len(arguments)}"
            )

        child = self._child_context()

        for name, value in zip(
            self.parameters,
            arguments,
        ):
            child.set_variable(name, value)

        from core.interpreter.interpreter import Interpreter

        return Interpreter(child).evaluate(self.body)

    def _child_context(self):
        parent = self.closure_context
        child = parent.__class__.__new__(parent.__class__)

        child.variables = dict(self.closure_variables)
        child.functions = parent.functions
        child.plot_engine = parent.plot_engine
        child.call_stack = parent.call_stack
        child.display_format = parent.display_format
        child.current_working_directory = (
            parent.current_working_directory
        )
        child.search_paths = parent.search_paths
        child.library_paths = parent.library_paths
        child.function_resolver = parent.function_resolver
        child.help_database = parent.help_database
        child.file_function_stack = parent.file_function_stack
        child.current_source_path = parent.current_source_path
        child.path_changed_callback = (
            parent.path_changed_callback
        )
        child.output_callback = parent.output_callback
        child.input_callback = parent.input_callback
        child.debugger = parent.debugger

        return child

    def __repr__(self):
        return str(self)

    def __str__(self):
        return (
            "@("
            + ", ".join(self.parameters)
            + ") <expression>"
        )
