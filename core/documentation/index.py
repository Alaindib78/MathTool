from collections import defaultdict

from core.documentation.search import HelpSearchEngine


class HelpIndex:
    def __init__(self, entries=None, search_engine=None):
        self.search_engine = search_engine or HelpSearchEngine()
        self.rebuild(entries or [])

    def rebuild(self, entries):
        self.entries = list(self.unique_entries(entries))
        self.by_key = {}
        self.categories = defaultdict(list)
        self.alphabetical = defaultdict(list)

        for entry in self.entries:
            self.add_key(entry.functionName, entry)

            for alias in entry.aliases:
                self.add_key(alias, entry)

            if entry.title:
                self.add_key(entry.title, entry)

            self.categories[entry.category].append(entry)

            letter = self.index_letter(entry.display_name)
            self.alphabetical[letter].append(entry)

        for category in self.categories:
            self.categories[category].sort(
                key=lambda entry: entry.display_name.lower()
            )

        for letter in self.alphabetical:
            self.alphabetical[letter].sort(
                key=lambda entry: entry.display_name.lower()
            )

    def unique_entries(self, entries):
        seen = set()

        for entry in entries:
            key = entry.functionName.lower()

            if key in seen:
                continue

            seen.add(key)
            yield entry

    def add_key(self, key, entry):
        normalized = self.normalize_key(key)

        if normalized:
            self.by_key[normalized] = entry

    def normalize_key(self, key):
        return str(key or "").strip().lower()

    def index_letter(self, text):
        for char in str(text or "").strip().upper():
            if "A" <= char <= "Z":
                return char

            if char.isdigit():
                return "#"

        return "#"

    def all_entries(self):
        return sorted(
            self.entries,
            key=lambda entry: entry.display_name.lower(),
        )

    def get(self, name):
        return self.by_key.get(
            self.normalize_key(name)
        )

    def search(self, query):
        return self.search_engine.search(
            self.entries,
            query,
        )

    def entries_by_category(self):
        return {
            category: list(entries)
            for category, entries in sorted(
                self.categories.items(),
                key=lambda item: item[0].lower(),
            )
        }

    def entries_by_letter(self):
        return {
            letter: list(self.alphabetical[letter])
            for letter in sorted(self.alphabetical)
        }
