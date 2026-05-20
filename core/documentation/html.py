import html
import re


FENCE_RE = re.compile(r"^\s*```")


def function_help_to_html(function_help):
    body = render_rich_text(function_help.fullText)

    see_also = ""

    if function_help.seeAlso:
        links = [
            (
                f'<a href="seealso:{html.escape(name)}">'
                f"{html.escape(name)}</a>"
            )
            for name in function_help.seeAlso
        ]
        see_also = (
            "<h3>See Also</h3><p>"
            + ", ".join(links)
            + "</p>"
        )

    return f"""
    <html>
    <head>
    <style>
      body {{
        color: #d4d4d4;
        background: #1e1e1e;
        font-family: Segoe UI, Arial, sans-serif;
        font-size: 10pt;
      }}
      h2 {{
        color: #ffffff;
        margin-bottom: 4px;
      }}
      h3 {{
        color: #dcdcdc;
        margin-top: 18px;
      }}
      .signature {{
        color: #dcdcdc;
        background: #252526;
        border: 1px solid #3e3e42;
        padding: 8px;
        font-family: Consolas, monospace;
        white-space: pre-wrap;
      }}
      pre {{
        color: #d4d4d4;
        background: #252526;
        border: 1px solid #3e3e42;
        padding: 8px;
        font-family: Consolas, monospace;
        white-space: pre-wrap;
      }}
      code {{
        color: #dcdcdc;
        background: #252526;
        font-family: Consolas, monospace;
      }}
      a {{
        color: #4fc3f7;
        text-decoration: none;
      }}
      li {{
        margin-bottom: 4px;
      }}
    </style>
    </head>
    <body>
      <h2>{html.escape(function_help.functionName)}</h2>
      <div class="signature">{html.escape(function_help.signature)}</div>
      {body}
      {see_also}
    </body>
    </html>
    """


def render_rich_text(text):
    lines = text.splitlines()
    blocks = []
    paragraph = []
    code = []
    bullets = []
    in_fence = False

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

    for line in lines:
        stripped = line.strip()

        if FENCE_RE.match(line):
            flush_paragraph()
            flush_bullets()

            if in_fence:
                flush_code()
            in_fence = not in_fence
            continue

        if in_fence:
            code.append(line)
            continue

        if not stripped:
            flush_paragraph()
            flush_bullets()
            flush_code()
            continue

        if is_code_line(line):
            flush_paragraph()
            flush_bullets()
            code.append(line)
            continue

        if is_bullet_line(stripped):
            flush_paragraph()
            flush_code()
            bullets.append(stripped[1:].strip())
            continue

        if stripped.endswith(":") and len(stripped) < 40:
            flush_paragraph()
            flush_bullets()
            flush_code()
            blocks.append(f"<h3>{html.escape(stripped[:-1])}</h3>")
            continue

        flush_code()
        flush_bullets()
        paragraph.append(stripped)

    flush_paragraph()
    flush_bullets()
    flush_code()

    return "\n".join(blocks)


def is_code_line(line):
    return (
        line.startswith("    ")
        or line.startswith("\t")
        or line.startswith("  >>")
    )


def is_bullet_line(stripped):
    return stripped.startswith("- ") or stripped.startswith("* ")


def inline_markup(text):
    escaped = html.escape(text)

    return re.sub(
        r"`([^`]+)`",
        r"<code>\1</code>",
        escaped,
    )
