class ReturnException(Exception):
    def __init__(self, value=None, has_value=True):
        self.value = value
        self.has_value = has_value


class BreakException(Exception):
    pass


class ContinueException(Exception):
    pass
