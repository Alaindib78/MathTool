from core.documentation.models import FunctionHelp


def format_function_help(function_help):
    lines = [
        function_help.functionName,
        "-" * len(function_help.functionName),
    ]

    if function_help.signature:
        lines.extend(
            [
                "Signature:",
                f"  {function_help.signature}",
                "",
            ]
        )

    if function_help.fullText:
        lines.append(function_help.fullText.rstrip())

    if function_help.seeAlso and "see also" not in function_help.fullText.lower():
        lines.extend(
            [
                "",
                "See also: " + ", ".join(function_help.seeAlso),
            ]
        )

    return "\n".join(lines).rstrip()


def format_help_overview(entries):
    lines = [
        "MathTool help",
        "=============",
        "",
        "Use help functionName or help('functionName') for details.",
        "Use lookfor keyword to search H1 lines and descriptions.",
        "",
        "Available topics:",
    ]

    for entry in entries:
        suffix = f" - {entry.h1Line}" if entry.h1Line else ""
        lines.append(f"  {entry.functionName}{suffix}")

    return "\n".join(lines)


def format_no_help(topic):
    return f"No help available for {topic}"


def format_lookfor_results(keyword, results):
    if not results:
        return f"No matches found for {keyword}"

    lines = [
        f"Search results for {keyword}:",
        "",
    ]

    for entry in results:
        description = entry.h1Line or "No description available."
        lines.append(f"  {entry.functionName} - {description}")

    return "\n".join(lines)


def builtin_help_from_entry(name, entry):
    signatures = entry.get("signatures", [])
    signature = signatures[0] if signatures else name

    full_lines = [
        f"Definition: {entry.get('summary', '')}",
        "",
        "Syntax:",
    ]

    for item in signatures:
        full_lines.append(f"  {item}")

    full_lines.extend(
        [
            "",
            f"Inputs: {entry.get('inputs', '')}",
            f"Output: {entry.get('output', '')}",
            f"Options: {entry.get('options', '')}",
        ]
    )

    examples = entry.get("examples", [])

    if examples:
        full_lines.append("")
        full_lines.append("Examples:")

        for example in examples:
            full_lines.append(f"  {example}")

    see_also = entry.get("see_also", [])

    if see_also:
        full_lines.append("")
        full_lines.append(
            "See also: " + ", ".join(see_also)
        )

    return FunctionHelp(
        functionName=name,
        signature=signature,
        h1Line=entry.get("summary", ""),
        fullText="\n".join(full_lines).rstrip(),
        examples=list(examples),
        seeAlso=list(see_also),
        sourcePath=None,
        isBuiltin=True,
    )
