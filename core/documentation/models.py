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
