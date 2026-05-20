import re
from pathlib import Path

from core.documentation.models import FunctionHelp


FUNCTION_DEFINITION_RE = re.compile(
    r"^\s*function\s+"
    r"(?:(?P<returns>\[[^\]]+\]|[A-Za-z_][A-Za-z0-9_]*)"
    r"\s*=\s*)?"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
    r"\s*(?:\((?P<params>[^)]*)\))?"
)

COMMENT_RE = re.compile(r"^\s*%(?P<text>.*)$")

SEE_ALSO_RE = re.compile(
    r"^\s*see\s+also\s+(?P<names>.+)$",
    re.IGNORECASE,
)

SECTION_RE = re.compile(r"^\s*[A-Za-z][A-Za-z ]+:\s*$")


def parse_function_help(source, source_path=None):
    lines = source.splitlines()
    entries = []

    for index, line in enumerate(lines):
        match = FUNCTION_DEFINITION_RE.match(line)

        if not match:
            continue

        documentation = help_comment_block(
            lines,
            index + 1,
        )

        if not documentation:
            continue

        function_name = match.group("name")

        entries.append(
            FunctionHelp(
                functionName=function_name,
                signature=line.strip(),
                h1Line=h1_line(documentation),
                fullText="\n".join(documentation).rstrip(),
                examples=examples_from_help(documentation),
                seeAlso=see_also_from_help(documentation),
                sourcePath=source_path,
                isBuiltin=False,
            )
        )

    return entries


def parse_function_help_file(path):
    path = Path(path)
    source = path.read_text(encoding="utf-8")

    return parse_function_help(
        source,
        source_path=str(path.resolve()),
    )


def help_comment_block(lines, start_index):
    comments = []

    for line in lines[start_index:]:
        match = COMMENT_RE.match(line)

        if not match:
            break

        comments.append(
            normalize_comment_text(match.group("text"))
        )

    return comments


def normalize_comment_text(text):
    text = text.rstrip()

    if text.startswith(" "):
        return text[1:]

    return text


def h1_line(documentation):
    for line in documentation:
        stripped = line.strip()

        if stripped:
            return stripped

    return ""


def examples_from_help(documentation):
    examples = []
    current = []
    in_example_section = False

    for line in documentation:
        stripped = line.strip()

        if is_example_heading(stripped):
            if current:
                examples.append("\n".join(current).rstrip())
                current = []

            in_example_section = True
            continue

        if (
            in_example_section
            and stripped
            and (
                SECTION_RE.match(stripped)
                or SEE_ALSO_RE.match(stripped)
            )
        ):
            if current:
                examples.append("\n".join(current).rstrip())
                current = []

            in_example_section = False

        if in_example_section:
            current.append(line.rstrip())

    if current:
        examples.append("\n".join(current).rstrip())

    return [
        example
        for example in examples
        if example.strip()
    ]


def is_example_heading(text):
    return text.lower() in {
        "example:",
        "examples:",
    }


def see_also_from_help(documentation):
    names = []

    for line in documentation:
        match = SEE_ALSO_RE.match(line)

        if not match:
            continue

        for name in re.split(r"[\s,]+", match.group("names")):
            cleaned = name.strip().strip(".;")

            if cleaned:
                names.append(cleaned)

    return names
