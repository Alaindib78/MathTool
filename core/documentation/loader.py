from dataclasses import replace
from pathlib import Path
import re

from core.documentation.formatter import builtin_help_from_entry
from core.documentation.models import FunctionHelp
from core.documentation.parser import parse_function_help
from core.stdlib.help_text import HELP_CATEGORIES, HELP_TOPICS


FRONT_MATTER_BOUNDARY = "---"
HEADING_RE = re.compile(r"^\s*#\s+(?P<title>.+?)\s*$")
FENCE_RE = re.compile(r"^\s*```\s*(?P<language>[A-Za-z0-9_-]*)")
DOC_ID_RE = re.compile(r"[^a-z0-9]+")


def default_docs_directory():
    return Path(__file__).resolve().parents[2] / "docs"


def humanize_category(category):
    return str(category or "General").strip().title()


def topic_id_from_path(path):
    return DOC_ID_RE.sub(
        "-",
        path.stem.lower(),
    ).strip("-")


class DocumentationLoader:
    def __init__(self, context=None, docs_directories=None):
        self.context = context
        self.docs_directories = (
            list(docs_directories)
            if docs_directories is not None
            else [default_docs_directory()]
        )

    def load_builtin_entries(self):
        category_by_name = {}

        for category, names in HELP_CATEGORIES.items():
            for name in names:
                category_by_name[name.lower()] = (
                    humanize_category(category)
                )

        entries = []

        for name, data in HELP_TOPICS.items():
            category = category_by_name.get(
                name.lower(),
                "Builtin Functions",
            )
            keywords = [
                "builtin",
                category,
                *data.get("see_also", []),
            ]

            entries.append(
                replace(
                    builtin_help_from_entry(name, data),
                    category=category,
                    keywords=keywords,
                    kind="builtin",
                    aliases=[name.lower()],
                    title=name,
                )
            )

        return entries

    def markdown_signature(self):
        rows = []

        for path in self.markdown_files():
            try:
                stat = path.stat()
            except OSError:
                continue

            rows.append(
                (
                    str(path.resolve()),
                    stat.st_mtime_ns,
                    stat.st_size,
                )
            )

        return tuple(sorted(rows))

    def load_markdown_entries(self):
        entries = []

        for path in self.markdown_files():
            entry = self.parse_markdown_file(path)

            if entry is not None:
                entries.append(entry)

        return entries

    def markdown_files(self):
        files = []

        for directory in self.docs_directories:
            path = Path(directory)

            if not path.is_dir():
                continue

            try:
                files.extend(path.rglob("*.md"))
            except OSError:
                continue

        return sorted(
            files,
            key=lambda path: str(path).lower(),
        )

    def parse_markdown_file(self, path):
        path = Path(path)

        try:
            source = path.read_text(encoding="utf-8")
        except OSError:
            return None

        metadata, body = parse_front_matter(source)
        title = metadata.get("title") or first_heading(body) or path.stem
        topic_id = metadata.get("id") or topic_id_from_path(path)
        summary = (
            metadata.get("summary")
            or first_paragraph(body)
            or title
        )
        aliases = metadata_list(metadata, "aliases")
        aliases.extend(
            [
                title,
                title.replace(" ", "-"),
            ]
        )
        keywords = metadata_list(metadata, "keywords")
        related = metadata_list(metadata, "related")
        examples = examples_from_markdown(body)

        return FunctionHelp(
            functionName=topic_id,
            signature=metadata.get("syntax", ""),
            h1Line=summary,
            fullText=remove_leading_title(body, title),
            examples=examples,
            seeAlso=related,
            sourcePath=str(path.resolve()),
            isBuiltin=False,
            category=metadata.get("category", "General"),
            keywords=keywords,
            aliases=dedupe_strings(aliases),
            kind=metadata.get("kind", "guide"),
            title=title,
        )

    def current_function_signature(self):
        rows = []

        if self.context is None:
            return tuple()

        for _, directory in (
            self.context
            .function_resolver
            .directory_entries()
        ):
            for path in self.context.function_resolver.m_files(directory):
                try:
                    stat = path.stat()
                except OSError:
                    continue

                rows.append(
                    (
                        str(path.resolve()),
                        stat.st_mtime_ns,
                        stat.st_size,
                    )
                )

        return tuple(sorted(rows))

    def parse_function_file(self, path):
        try:
            source = Path(path).read_text(
                encoding="utf-8"
            )
        except OSError:
            return []

        entries = parse_function_help(
            source,
            source_path=path,
        )

        return [
            replace(
                entry,
                category="User Functions",
                keywords=[
                    "user function",
                    "function",
                    Path(path).stem,
                ],
                kind="function",
                title=entry.functionName,
            )
            for entry in entries
        ]


def parse_front_matter(source):
    lines = source.splitlines()

    if not lines or lines[0].strip() != FRONT_MATTER_BOUNDARY:
        return {}, source.strip()

    metadata_lines = []
    body_start = 0

    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == FRONT_MATTER_BOUNDARY:
            body_start = index + 1
            break

        metadata_lines.append(line)
    else:
        return {}, source.strip()

    metadata = {}

    for line in metadata_lines:
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        metadata[key.strip().lower()] = value.strip()

    return metadata, "\n".join(lines[body_start:]).strip()


def metadata_list(metadata, key):
    value = metadata.get(key, "")

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def first_heading(text):
    for line in text.splitlines():
        match = HEADING_RE.match(line)

        if match:
            return match.group("title").strip()

    return ""


def first_paragraph(text):
    lines = []

    for line in text.splitlines():
        stripped = line.strip()

        if not stripped:
            if lines:
                break

            continue

        if stripped.startswith("#"):
            continue

        if stripped.startswith("```"):
            break

        lines.append(strip_markdown(stripped))

    return " ".join(lines).strip()


def strip_markdown(text):
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.lstrip("-* ")

    return text.strip()


def remove_leading_title(body, title):
    lines = body.splitlines()

    for index, line in enumerate(lines):
        stripped = line.strip()

        if not stripped:
            continue

        match = HEADING_RE.match(stripped)

        if (
            match
            and match.group("title").strip().lower()
            == title.strip().lower()
        ):
            return "\n".join(lines[index + 1:]).strip()

        break

    return body.strip()


def examples_from_markdown(body):
    examples = []
    current = []
    in_fence = False
    current_language = ""

    for line in body.splitlines():
        match = FENCE_RE.match(line)

        if match:
            if in_fence:
                if current and example_language(current_language):
                    examples.append(
                        "\n".join(current).rstrip()
                    )

                current = []
                current_language = ""
                in_fence = False
            else:
                current_language = (
                    match.group("language") or ""
                ).lower()
                in_fence = True
            continue

        if in_fence:
            current.append(line)

    return [
        example
        for example in examples
        if example.strip()
    ]


def example_language(language):
    return language in {
        "",
        "m",
        "matlab",
        "mathtool",
    }


def dedupe_strings(items):
    result = []
    seen = set()

    for item in items:
        key = str(item).strip().lower()

        if not key or key in seen:
            continue

        seen.add(key)
        result.append(str(item).strip())

    return result
