from difflib import SequenceMatcher
import re


WORD_RE = re.compile(r"[a-z0-9]+")


def normalize(text):
    return " ".join(
        WORD_RE.findall(str(text or "").lower())
    )


def compact(text):
    return normalize(text).replace(" ", "")


def is_subsequence(needle, haystack):
    iterator = iter(haystack)

    return all(char in iterator for char in needle)


class HelpSearchEngine:
    def search(self, entries, query):
        query = normalize(query)

        if not query:
            return sorted(
                entries,
                key=lambda entry: entry.display_name.lower(),
            )

        scored = []

        for entry in entries:
            score = self.score(entry, query)

            if score > 0:
                scored.append((score, entry))

        return [
            entry
            for _, entry in sorted(
                scored,
                key=lambda item: (
                    -item[0],
                    item[1].display_name.lower(),
                ),
            )
        ]

    def score(self, entry, query):
        query_compact = compact(query)
        name = normalize(entry.functionName)
        title = normalize(entry.display_name)
        signature = normalize(entry.signature)
        summary = normalize(entry.h1Line)
        body = normalize(entry.fullText)
        category = normalize(entry.category)
        keywords = normalize(" ".join(entry.keywords))
        aliases = normalize(" ".join(entry.aliases))

        primary = [name, title, *aliases.split()]
        searchable = normalize(
            " ".join(entry.searchable_terms)
        )
        searchable_compact = compact(searchable)

        score = 0.0

        for value in primary:
            if not value:
                continue

            value_compact = compact(value)

            if query == value:
                score = max(score, 1200)
            elif value.startswith(query):
                score = max(score, 1000)
            elif value_compact.startswith(query_compact):
                score = max(score, 920)
            elif query in value:
                score = max(score, 800)
            elif query_compact in value_compact:
                score = max(score, 740)

        for value, weight in [
            (keywords, 700),
            (signature, 620),
            (summary, 540),
            (category, 420),
            (body, 260),
        ]:
            if not value:
                continue

            value_compact = compact(value)

            if query in value:
                score = max(score, weight)
            elif query_compact in value_compact:
                score = max(score, weight - 60)

        if score:
            return score

        if query_compact and len(query_compact) >= 2:
            for value in [name, title, keywords, summary]:
                value_compact = compact(value)

                if (
                    value_compact
                    and is_subsequence(
                        query_compact,
                        value_compact,
                    )
                ):
                    ratio = SequenceMatcher(
                        None,
                        query_compact,
                        value_compact,
                    ).ratio()

                    if ratio >= 0.35:
                        score = max(score, 180 + ratio * 180)

        if query_compact and query_compact in searchable_compact:
            score = max(score, 180)

        return score
