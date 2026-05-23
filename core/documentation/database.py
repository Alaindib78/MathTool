from core.documentation.formatter import (
    format_function_help,
    format_help_overview,
    format_lookfor_results,
    format_no_help,
)
from core.documentation.index import HelpIndex
from core.documentation.loader import DocumentationLoader
from core.documentation.search import HelpSearchEngine


class HelpManager:
    def __init__(self, context=None, docs_directories=None):
        self.context = context
        self.loader = DocumentationLoader(
            context,
            docs_directories=docs_directories,
        )
        self.search_engine = HelpSearchEngine()
        self.index = HelpIndex(
            [],
            search_engine=self.search_engine,
        )
        self.file_cache = {}
        self.builtin_entries = {}
        self.entries = {}
        self.scan_signature = None
        self.docs_signature = None

        self.refresh(force=True)

    def build_builtin_entries(self):
        return {
            entry.functionName.lower(): entry
            for entry in self.loader.load_builtin_entries()
        }

    def refresh(self, force=False):
        function_signature = (
            self.current_scan_signature()
        )
        docs_signature = self.loader.markdown_signature()

        if (
            not force
            and function_signature == self.scan_signature
            and docs_signature == self.docs_signature
        ):
            return

        self.builtin_entries = self.build_builtin_entries()
        entries = dict(self.builtin_entries)

        for entry in self.loader.load_markdown_entries():
            entries[entry.functionName.lower()] = entry

        live_paths = set()

        for path, modified_time, size in function_signature:
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
        self.index.rebuild(entries.values())
        self.scan_signature = function_signature
        self.docs_signature = docs_signature

    def current_scan_signature(self):
        return self.loader.current_function_signature()

    def parse_path(self, path):
        return self.loader.parse_function_file(path)

    def all_entries(self):
        self.refresh()

        return self.index.all_entries()

    def get(self, name):
        self.refresh()

        if name is None:
            return None

        return self.index.get(name)

    def search(self, query):
        self.refresh()

        return self.index.search(query)

    def entries_by_category(self):
        self.refresh()

        return self.index.entries_by_category()

    def entries_by_letter(self):
        self.refresh()

        return self.index.entries_by_letter()

    def popular_entries(self):
        self.refresh()

        names = [
            "plot",
            "sin",
            "cos",
            "zeros",
            "ones",
            "linspace",
            "eig",
            "solve",
            "figure",
            "help",
            "plotting-guide",
            "matrices",
            "shortcuts",
        ]
        entries = []
        seen = set()

        for name in names:
            entry = self.get(name)

            if entry is None:
                continue

            key = entry.functionName.lower()

            if key in seen:
                continue

            seen.add(key)
            entries.append(entry)

        return entries

    def lookfor(self, keyword):
        self.refresh()

        keyword = str(keyword or "").strip()
        lowered = keyword.lower()
        results = []

        for entry in self.index.all_entries():
            if (
                lowered in entry.h1Line.lower()
                or lowered in entry.fullText.lower()
                or lowered in " ".join(entry.keywords).lower()
            ):
                results.append(entry)

        return sorted(
            results,
            key=lambda entry: entry.display_name.lower(),
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


class FunctionHelpDatabase(HelpManager):
    pass
