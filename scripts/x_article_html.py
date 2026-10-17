#!/usr/bin/env python3
"""X Article source -> /tmp/x-article/<edition>.html for pasting into an X Article (docs/HANDOFF.md playbook).

Source: articles/x/<edition>/article.md (the single-lead-story X Article, docs/X_ARTICLE_STYLE.md) when it exists,
else the website roundup reports/<edition>.md (legacy fallback). Front matter is stripped; `title:` (and, for
article.md, `caption:`) come from it. Every non-empty line becomes its own <p>, so line breaks survive the paste.
Keeps links and **bold**, turns "- item" lines into "• item", "## Heading" into a bold paragraph, drops any line
containing "Mind Blow", and puts a word joiner after "$" before a digit (X turns "$3" into a cashtag link).
Prints TITLE, CAPTION, the HTML path and the localhost serve command."""
import html, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = "/tmp/x-article"; PORT = 8765
DOLLAR = re.compile(r"\$\s?\d")

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{html.escape(html.unescape(m[2]))}">{m[1]}</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    # dollar-sign guard: a word joiner after $ keeps "$3" plain text on X (tags/URLs are skipped)
    return re.sub(r"(<[^>]*>)|\$(?=\s?\d)", lambda m: m[1] or "$\u2060", t)

def plain(t):
    return re.sub(r"\s+", " ", re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t).replace("*", "").replace("`", "")).strip()

def hook_caption(first, limit=200):
    # fallback hook = first sentence of the opening line, plain text, cut at a word boundary, ending in "..."
    s = re.split(r"(?<=[.!?])\s", plain(first))[0].rstrip(".!? ")
    if len(s) > limit: s = s[:limit].rsplit(" ", 1)[0].rstrip(",;: ")
    return s + "..."

def front_matter(text):
    fm = {}
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m: return fm, text
    for line in m[1].splitlines():
        k, _, v = line.partition(":")
        if k.strip(): fm[k.strip()] = v.strip().strip('"')
    return fm, text[m.end():]

def to_p(line):
    s = line.strip()
    h = re.match(r"#{1,6}\s+(.*)", s)
    if h: return f"<p><strong>{inline(h[1].strip('* '))}</strong></p>"
    b = re.match(r"[-*]\s+(.*)", s)
    if b: return f"<p>\u2022 {inline(b[1])}</p>"
    return f"<p>{inline(s)}</p>"

def problems(title, caption):
    out = []
    for name, v in (("title", title), ("caption", caption)):
        if "mind blow" in v.lower(): out.append(f"{name} contains 'Mind Blow'")
        if DOLLAR.search(v): out.append(f"{name} has '$' followed by a number (write '3 dollars')")
    if not caption.endswith("..."): out.append("caption must end with '...'")
    return out

def main():
    if len(sys.argv) != 2: sys.exit("usage: ./run.sh x-article <edition>")
    ed = sys.argv[1]
    art, rep = f"{ROOT}/articles/x/{ed}/article.md", f"{ROOT}/reports/{ed}.md"
    src = art if os.path.exists(art) else rep
    if not os.path.exists(src): sys.exit(f"missing {art} and {rep}")
    fm, text = front_matter(open(src, encoding="utf-8").read())
    lines = [l for l in text.splitlines() if l.strip() and "mind blow" not in l.lower()]
    title = fm.get("title", ed)
    body_lines = [l for l in lines if not re.match(r"\s*#{1,6}\s", l)]
    caption = fm.get("caption") or hook_caption(body_lines[0] if body_lines else "")
    issues = problems(title, caption)
    if src == art and issues:
        sys.exit(f"{os.path.relpath(art, ROOT)}: " + "; ".join(issues))
    body = [to_p(l) for l in lines]  # dek omitted: X auto-links it oddly and it repeats the opening
    os.makedirs(OUT, exist_ok=True); out = f"{OUT}/{ed}.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(f'<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(title)}</title></head>\n'
                f'<body><div id="article">\n' + "\n".join(body) + "\n</div></body></html>\n")
    words = len(plain(" ".join(lines)).split())
    print(f"SOURCE: {os.path.relpath(src, ROOT)}" + ("" if src == art else "  (FALLBACK: no articles/x/<edition>/article.md; this is the roundup)"))
    print(f"TITLE: {title}\nCAPTION: {caption}")
    if src != art:
        print("  (suggestion: lead with the most useful actionable dev/DevOps takeaway, not spec numbers; keep the trailing ...)")
        for i in issues: print(f"  WARNING: {i}")
    print(f"HTML: {out} ({len(body)} paragraphs, ~{words} words)")
    print(f"SERVE: python3 -m http.server {PORT} --bind 127.0.0.1 -d {OUT}  ->  http://127.0.0.1:{PORT}/{ed}.html")

if __name__ == "__main__": main()
