from dataclasses import dataclass, field


@dataclass(frozen=True)
class FunctionHelp:
    functionName: str
    signature: str
    h1Line: str
    fullText: str
    examples: list[str] = field(default_factory=list)
    seeAlso: list[str] = field(default_factory=list)
    sourcePath: str | None = None
    isBuiltin: bool = False
    category: str = "Builtin Functions"
    keywords: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    kind: str = "function"
    title: str | None = None

    @property
    def topic_id(self):
        return self.functionName.strip().lower()

    @property
    def display_name(self):
        return self.title or self.functionName

    @property
    def searchable_terms(self):
        return [
            self.functionName,
            self.display_name,
            self.signature,
            self.h1Line,
            self.fullText,
            *self.keywords,
            *self.aliases,
            *self.seeAlso,
            self.category,
            self.kind,
        ]
