#!/usr/bin/env python3
"""X Article source -> /tmp/x-article/<edition>.html for pasting into an X Article (docs/HANDOFF.md playbook).

Usage: x_article_html.py <edition> [--format roundup|deep-dive]   (docs/X_ARTICLE_STYLE.md "Formats")
  roundup    the classic digest Article: reports/<edition>.md (the website roundup, STYLE.md), one <p> per
             paragraph, dek omitted. Caption: "caption:" line of articles/x/<edition>/format.txt (guarded),
             else suggested from the first cold-open sentence (rewrite it tip-first).
  deep-dive  the four-step single-lead Article: articles/x/<edition>/article.md, every non-empty line its own <p>,
             "- item" -> "• item", "## Label" -> bold line; title and caption from its front matter, and it refuses
             a title/caption with "$<digit>" or "Mind Blow" or a caption not ending in "...".
  default    the first word of articles/x/<edition>/format.txt (the routine's recorded choice) if present, else
             deep-dive if articles/x/<edition>/article.md exists, else roundup.
Both: links, **bold** and `code` kept, lines containing "Mind Blow" dropped, word joiner after "$" before a digit
(X turns "$3" into a cashtag link). Prints FORMAT, SOURCE, TITLE, CAPTION, the HTML path and the serve command."""
import html, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = "/tmp/x-article"; PORT = 8765
DOLLAR = re.compile(r"\$\s?\d")

def inline(t, deep=True):
    t = html.escape(t, quote=False)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{html.escape(html.unescape(m[2]))}">{m[1]}</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", t)
    if deep: t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)  # roundup keeps its classic output byte for byte
    # dollar-sign guard: a word joiner after $ keeps "$3" plain text on X (tags/URLs are skipped)
    return re.sub(r"(<[^>]*>)|\$(?=\s?\d)" if deep else r"(<[^>]*>)|\$(?=\d)", lambda m: m[1] or "$\u2060", t)

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
    args = sys.argv[1:]; fmt = None
    if "--format" in args:
        i = args.index("--format"); fmt = (args[i + 1] if i + 1 < len(args) else ""); del args[i:i + 2]
    elif any(a.startswith("--format=") for a in args):
        a = next(a for a in args if a.startswith("--format=")); fmt = a.split("=", 1)[1]; args.remove(a)
    if len(args) != 1 or fmt not in (None, "roundup", "deep-dive"):
        sys.exit("usage: ./run.sh x-article <edition> [--format roundup|deep-dive]")
    ed = args[0]
    art, rep = f"{ROOT}/articles/x/{ed}/article.md", f"{ROOT}/reports/{ed}.md"
    choice = f"{ROOT}/articles/x/{ed}/format.txt"
    chosen_caption = ""
    if os.path.exists(choice):
        m = re.search(r"^caption:\s*(.+)$", open(choice, encoding="utf-8").read(), re.M)
        if m: chosen_caption = m[1].strip().strip('"')
    if not fmt and os.path.exists(choice):
        fmt = (open(choice).read().split() or [""])[0]
        if fmt not in ("roundup", "deep-dive"): sys.exit(f"{os.path.relpath(choice, ROOT)}: first word must be roundup or deep-dive")
    fmt = fmt or ("deep-dive" if os.path.exists(art) else "roundup")
    src = art if fmt == "deep-dive" else rep
    if not os.path.exists(src):
        sys.exit(f"missing {os.path.relpath(src, ROOT)}" + (" (write it with the four steps in docs/X_ARTICLE_STYLE.md, or use --format roundup)" if fmt == "deep-dive" else " (run ./run.sh render first)"))
    fm, text = front_matter(open(src, encoding="utf-8").read())
    lines = [l for l in text.splitlines() if "mind blow" not in l.lower()]
    title = fm.get("title", ed)
    if fmt == "roundup":
        # unchanged classic behaviour: one <p> per blank-line paragraph, dek omitted (X auto-links it oddly and it
        # repeats the cold open), caption suggested from the first cold-open sentence
        paras = [p.strip() for p in re.split(r"\n\s*\n", "\n".join(lines)) if p.strip()]
        if "mind blow" in title.lower(): sys.exit("title contains 'Mind Blow': fix the article first")
        caption = chosen_caption or hook_caption(paras[0] if paras else "")
        body = [f"<p>{inline(p, deep=False)}</p>" for p in paras]
    else:
        lines = [l for l in lines if l.strip()]
        body_lines = [l for l in lines if not re.match(r"\s*#{1,6}\s", l)]
        caption = fm.get("caption") or hook_caption(body_lines[0] if body_lines else "")
        body = [to_p(l) for l in lines]
    issues = problems(title, caption)
    if fmt == "deep-dive" and issues:
        sys.exit(f"{os.path.relpath(art, ROOT)}: " + "; ".join(issues))
    if fmt == "roundup" and chosen_caption and (bad := [i for i in issues if i.startswith("caption")]):
        sys.exit(f"{os.path.relpath(choice, ROOT)}: " + "; ".join(bad))
    os.makedirs(OUT, exist_ok=True); out = f"{OUT}/{ed}.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(f'<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(title)}</title></head>\n'
                f'<body><div id="article">\n' + "\n".join(body) + "\n</div></body></html>\n")
    words = len(plain(" ".join(lines)).split())
    print(f"FORMAT: {fmt}   (record it as \"format\": \"{fmt}\" in state/x_posts.json)")
    print(f"SOURCE: {os.path.relpath(src, ROOT)}")
    print(f"TITLE: {title}\nCAPTION: {caption}")
    if fmt == "roundup" and not chosen_caption:
        print("  (suggestion only: rewrite it to lead with the single most useful actionable dev/DevOps tip, not spec numbers; keep the trailing ...)")
        for i in issues: print(f"  WARNING: {i}")
    print(f"HTML: {out} ({len(body)} paragraphs, ~{words} words)")
    print(f"SERVE: python3 -m http.server {PORT} --bind 127.0.0.1 -d {OUT}  ->  http://127.0.0.1:{PORT}/{ed}.html")

if __name__ == "__main__": main()
