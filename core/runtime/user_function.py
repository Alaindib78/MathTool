class UserFunction:
    def __init__(
        self,
        declaration,
        closure_context,
        source_path=None,
        local_functions=None,
    ):
        self.declaration = declaration
        self.closure_context = closure_context
        self.source_path = source_path
        self.local_functions = local_functions or {}
