from pathlib import Path

from core.documentation.formatter import (
    builtin_help_from_entry,
    format_function_help,
    format_help_overview,
    format_lookfor_results,
    format_no_help,
)
from core.documentation.parser import parse_function_help
from core.stdlib.help_text import HELP_TOPICS


class FunctionHelpDatabase:
    def __init__(self, context=None):
        self.context = context
        self.builtin_entries = self.build_builtin_entries()
        self.file_cache = {}
        self.entries = dict(self.builtin_entries)
        self.scan_signature = None

    def build_builtin_entries(self):
        return {
            name.lower(): builtin_help_from_entry(
                name,
                entry,
            )
            for name, entry in HELP_TOPICS.items()
        }

    def refresh(self, force=False):
        if self.context is None:
            return

        signature = self.current_scan_signature()

        if not force and signature == self.scan_signature:
            return

        entries = dict(self.builtin_entries)
        live_paths = set()

        for path, modified_time, size in signature:
            live_paths.add(path)
            cached = self.file_cache.get(path)

            if (
                cached is None
                or cached["modified_time"] != modified_time
                or cached["size"] != size
            ):
                cached = {
                    "modified_time": modified_time,
                    "size": size,
                    "entries": self.parse_path(path),
                }
                self.file_cache[path] = cached

            for entry in cached["entries"]:
                entries[entry.functionName.lower()] = entry

        for path in list(self.file_cache):
            if path not in live_paths:
                del self.file_cache[path]

        self.entries = entries
        self.scan_signature = signature

    def current_scan_signature(self):
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

    def parse_path(self, path):
        try:
            source = Path(path).read_text(
                encoding="utf-8"
            )
        except OSError:
            return []

        return parse_function_help(
            source,
            source_path=path,
        )

    def all_entries(self):
        self.refresh()

        return sorted(
            self.entries.values(),
            key=lambda entry: entry.functionName.lower(),
        )

    def get(self, name):
        self.refresh()

        if name is None:
            return None

        return self.entries.get(
            str(name).strip().lower()
        )

    def search(self, query):
        self.refresh()

        query = str(query or "").strip().lower()

        if not query:
            return self.all_entries()

        results = []

        for entry in self.entries.values():
            haystack = "\n".join(
                [
                    entry.functionName,
                    entry.h1Line,
                    entry.fullText,
                ]
            ).lower()

            if query in haystack:
                results.append(entry)

        return sorted(
            results,
            key=lambda entry: (
                query not in entry.functionName.lower(),
                entry.functionName.lower(),
            ),
        )

    def lookfor(self, keyword):
        self.refresh()

        keyword = str(keyword or "").strip()
        lowered = keyword.lower()
        results = []

        for entry in self.entries.values():
            if (
                lowered in entry.h1Line.lower()
                or lowered in entry.fullText.lower()
            ):
                results.append(entry)

        return sorted(
            results,
            key=lambda entry: entry.functionName.lower(),
        )

    def format_help(self, topic=None):
        self.refresh()

        if topic is None or str(topic).strip() == "":
            return format_help_overview(self.all_entries())

        entry = self.get(topic)

        if entry is None:
            return format_no_help(topic)

        return format_function_help(entry)

    def format_lookfor(self, keyword):
        return format_lookfor_results(
            keyword,
            self.lookfor(keyword),
        )
