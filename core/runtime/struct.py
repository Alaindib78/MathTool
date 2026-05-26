class MatlabStruct(dict):
    """Dictionary-backed MATLAB-style scalar struct."""


def is_struct(value):
    return isinstance(value, dict)


def missing_field_message(field_name):
    return f"Reference to non-existent field '{field_name}'"
