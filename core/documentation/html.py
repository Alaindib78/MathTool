import html
import re


FENCE_RE = re.compile(r"^\s*```\s*(?P<language>[A-Za-z0-9_-]*)")
HEADING_RE = re.compile(r"^\s*(#{1,4})\s+(?P<text>.+?)\s*$")
TABLE_DIVIDER_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def function_help_to_html(function_help):
    return topic_to_html(function_help)


def topic_to_html(topic):
    body = render_rich_text(topic.fullText)
    signature = ""

    if topic.signature:
        signature = (
            '<div class="signature">'
            + html.escape(topic.signature)
            + "</div>"
        )

    examples = ""

    if (
        topic.examples
        and "examples:" not in topic.fullText.lower()
        and "example:" not in topic.fullText.lower()
    ):
        snippets = "".join(
            "<pre>"
            + html.escape(example)
            + "</pre>"
            for example in topic.examples
        )
        examples = f"<h3>Examples</h3>{snippets}"

    see_also = ""

    if topic.seeAlso:
        links = [
            (
                f'<a href="topic:{html.escape(name)}">'
                f"{html.escape(name)}</a>"
            )
            for name in topic.seeAlso
        ]
        see_also = (
            "<h3>Related Topics</h3><p>"
            + ", ".join(links)
            + "</p>"
        )

    source = ""

    if topic.sourcePath:
        source = (
            '<p class="source">Source: '
            + html.escape(topic.sourcePath)
            + "</p>"
        )

    content = f"""
      <div class="eyebrow">{html.escape(topic.category)}</div>
      <h1>{html.escape(topic.display_name)}</h1>
      <p class="summary">{html.escape(topic.h1Line)}</p>
      {signature}
      {body}
      {examples}
      {see_also}
      {source}
    """

    return document_html(topic.display_name, content)


def help_home_to_html(help_database, recent_topics=None):
    recent_topics = recent_topics or []
    categories = help_database.entries_by_category()
    popular = help_database.popular_entries()

    quick_links = [
        ("Language Basics", "language-basics"),
        ("Matrices", "matrices"),
        ("Plotting Guide", "plotting-guide"),
        ("Builtin Functions", "help"),
        ("Examples", "examples"),
        ("Shortcuts", "shortcuts"),
    ]

    quick_html = "".join(
        tile_html(label, f"topic:{topic}")
        for label, topic in quick_links
    )
    popular_html = "".join(
        tile_html(entry.display_name, f"topic:{entry.functionName}")
        for entry in popular
    )
    category_html = "".join(
        tile_html(
            category,
            f"category:{category}",
            f"{len(entries)} topics",
        )
        for category, entries in categories.items()
    )

    if recent_topics:
        recent_html = "".join(
            tile_html(
                entry.display_name,
                f"topic:{entry.functionName}",
                entry.category,
            )
            for entry in recent_topics
        )
    else:
        recent_html = (
            '<p class="muted">Recently opened topics appear here.</p>'
        )

    content = f"""
      <div class="eyebrow">MathTool Documentation</div>
      <h1>Help Home</h1>
      <p class="summary">
        Search commands, language guides, examples, IDE features,
        and documented functions from the active path.
      </p>

      <h2>Quick Links</h2>
      <div class="tile-grid">{quick_html}</div>

      <h2>Popular Commands</h2>
      <div class="tile-grid">{popular_html}</div>

      <h2>Categories</h2>
      <div class="tile-grid">{category_html}</div>

      <h2>Recent Topics</h2>
      <div class="tile-grid">{recent_html}</div>
    """

    return document_html("Help Home", content)


def tile_html(title, href, subtitle=""):
    subtitle_html = (
        f'<span class="tile-subtitle">{html.escape(subtitle)}</span>'
        if subtitle
        else ""
    )

    return (
        f'<a class="tile" href="{html.escape(href)}">'
        f"<span>{html.escape(title)}</span>"
        f"{subtitle_html}"
        "</a>"
    )


def document_html(title, content):
    return f"""
    <html>
    <head>
    <meta charset="utf-8">
    <title>{html.escape(title)}</title>
    <style>
      body {{
        color: #d4d4d4;
        background: #1e1e1e;
        font-family: Segoe UI, Arial, sans-serif;
        font-size: 10pt;
        line-height: 1.45;
      }}
      h1 {{
        color: #ffffff;
        font-size: 24px;
        margin: 2px 0 6px 0;
      }}
      h2 {{
        color: #ffffff;
        font-size: 18px;
        margin: 22px 0 8px 0;
      }}
      h3 {{
        color: #dcdcdc;
        font-size: 14px;
        margin: 18px 0 6px 0;
      }}
      h4 {{
        color: #dcdcdc;
        font-size: 12px;
        margin: 14px 0 4px 0;
      }}
      p {{
        margin: 8px 0;
      }}
      .eyebrow {{
        color: #9cdcfe;
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0;
      }}
      .summary {{
        color: #c8c8c8;
        font-size: 12pt;
        margin-bottom: 12px;
      }}
      .signature, pre {{
        color: #d4d4d4;
        background: #252526;
        border: 1px solid #3e3e42;
        border-radius: 4px;
        padding: 9px;
        font-family: Consolas, "Courier New", monospace;
        white-space: pre-wrap;
      }}
      code {{
        color: #dcdcdc;
        background: #252526;
        font-family: Consolas, "Courier New", monospace;
        padding: 1px 4px;
      }}
      a {{
        color: #4fc3f7;
        text-decoration: none;
      }}
      ul, ol {{
        margin-top: 6px;
      }}
      li {{
        margin-bottom: 4px;
      }}
      table {{
        border-collapse: collapse;
        margin: 10px 0;
        width: 100%;
      }}
      th, td {{
        border: 1px solid #3e3e42;
        padding: 6px 8px;
      }}
      th {{
        background: #2d2d30;
        color: #ffffff;
      }}
      td {{
        background: #252526;
      }}
      img {{
        max-width: 100%;
      }}
      .source, .muted {{
        color: #9a9a9a;
        font-size: 9pt;
      }}
      .tile-grid {{
        margin-top: 6px;
      }}
      .tile {{
        display: inline-block;
        min-width: 150px;
        max-width: 230px;
        min-height: 42px;
        margin: 0 8px 8px 0;
        padding: 10px 12px;
        border: 1px solid #3e3e42;
        border-radius: 6px;
        background: #252526;
        color: #ffffff;
      }}
      .tile-subtitle {{
        display: block;
        color: #a8a8a8;
        font-size: 9pt;
        margin-top: 3px;
      }}
    </style>
    </head>
    <body>
      {content}
    </body>
    </html>
    """


def render_rich_text(text):
    lines = text.splitlines()
    blocks = []
    paragraph = []
    code = []
    bullets = []
    numbers = []
    in_fence = False
    index = 0

    def flush_paragraph():
        if paragraph:
            blocks.append(
                "<p>"
                + inline_markup(" ".join(paragraph))
                + "</p>"
            )
            paragraph.clear()

    def flush_code():
        if code:
            blocks.append(
                "<pre>"
                + html.escape("\n".join(code).rstrip())
                + "</pre>"
            )
            code.clear()

    def flush_bullets():
        if bullets:
            items = "".join(
                f"<li>{inline_markup(item)}</li>"
                for item in bullets
            )
            blocks.append(f"<ul>{items}</ul>")
            bullets.clear()

    def flush_numbers():
        if numbers:
            items = "".join(
                f"<li>{inline_markup(item)}</li>"
                for item in numbers
            )
            blocks.append(f"<ol>{items}</ol>")
            numbers.clear()

    def flush_all_text():
        flush_paragraph()
        flush_bullets()
        flush_numbers()
        flush_code()

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if FENCE_RE.match(line):
            flush_paragraph()
            flush_bullets()
            flush_numbers()

            if in_fence:
                flush_code()

            in_fence = not in_fence
            index += 1
            continue

        if in_fence:
            code.append(line)
            index += 1
            continue

        if not stripped:
            flush_all_text()
            index += 1
            continue

        if is_table_start(lines, index):
            flush_all_text()
            table_lines = [line]
            index += 2

            while index < len(lines) and "|" in lines[index]:
                table_lines.append(lines[index])
                index += 1

            blocks.append(render_table(table_lines))
            continue

        heading = HEADING_RE.match(line)

        if heading:
            flush_all_text()
            level = min(len(heading.group(1)) + 1, 4)
            blocks.append(
                f"<h{level}>"
                + inline_markup(heading.group("text").strip())
                + f"</h{level}>"
            )
            index += 1
            continue

        if is_code_line(line):
            flush_paragraph()
            flush_bullets()
            flush_numbers()
            code.append(line)
            index += 1
            continue

        if is_bullet_line(stripped):
            flush_paragraph()
            flush_code()
            flush_numbers()
            bullets.append(stripped[1:].strip())
            index += 1
            continue

        if is_numbered_line(stripped):
            flush_paragraph()
            flush_code()
            flush_bullets()
            numbers.append(
                re.sub(r"^\d+\.\s+", "", stripped)
            )
            index += 1
            continue

        if stripped.endswith(":") and len(stripped) < 44:
            flush_all_text()
            blocks.append(f"<h3>{html.escape(stripped[:-1])}</h3>")
            index += 1
            continue

        flush_code()
        flush_bullets()
        flush_numbers()
        paragraph.append(stripped)
        index += 1

    flush_all_text()

    return "\n".join(blocks)


def is_table_start(lines, index):
    return (
        "|" in lines[index]
        and index + 1 < len(lines)
        and TABLE_DIVIDER_RE.match(lines[index + 1])
    )


def render_table(lines):
    rows = [
        split_table_row(line)
        for line in lines
    ]

    if not rows:
        return ""

    header = rows[0]
    body = rows[1:]
    header_html = "".join(
        f"<th>{inline_markup(cell)}</th>"
        for cell in header
    )
    body_html = ""

    for row in body:
        body_html += (
            "<tr>"
            + "".join(
                f"<td>{inline_markup(cell)}</td>"
                for cell in row
            )
            + "</tr>"
        )

    return (
        "<table><thead><tr>"
        + header_html
        + "</tr></thead><tbody>"
        + body_html
        + "</tbody></table>"
    )


def split_table_row(line):
    stripped = line.strip().strip("|")

    return [
        cell.strip()
        for cell in stripped.split("|")
    ]


def is_code_line(line):
    return (
        line.startswith("    ")
        or line.startswith("\t")
        or line.startswith("  >>")
    )


def is_bullet_line(stripped):
    return stripped.startswith("- ") or stripped.startswith("* ")


def is_numbered_line(stripped):
    return re.match(r"^\d+\.\s+", stripped) is not None


def inline_markup(text):
    escaped = html.escape(text)
    escaped = IMAGE_RE.sub(image_markup, escaped)
    escaped = LINK_RE.sub(link_markup, escaped)

    return re.sub(
        r"`([^`]+)`",
        r"<code>\1</code>",
        escaped,
    )


def image_markup(match):
    alt = html.escape(match.group(1))
    src = html.escape(match.group(2))

    return f'<img alt="{alt}" src="{src}">'


def link_markup(match):
    label = match.group(1)
    target = match.group(2).strip()
    href = normalize_href(target)

    return (
        f'<a href="{html.escape(href)}">'
        f"{label}</a>"
    )


def normalize_href(target):
    lowered = target.lower()

    if (
        ":" in target
        or lowered.startswith("http://")
        or lowered.startswith("https://")
        or target.startswith("#")
    ):
        return target

    return f"topic:{target}"
