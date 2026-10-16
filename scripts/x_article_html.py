#!/usr/bin/env python3
"""reports/<edition>.md -> /tmp/x-article/<edition>.html for pasting into an X Article (docs/HANDOFF.md).
Strips front matter, drops any line containing "Mind Blow", keeps links, prints title, hook caption, serve cmd."""
import html, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = "/tmp/x-article"; PORT = 8765

def inline(t):
    t = html.escape(t, quote=False)
    # X turns "$3" into a cashtag/stock link; a word joiner after $ keeps it plain text
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{html.escape(html.unescape(m[2]))}">{m[1]}</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", t)
    return re.sub(r"(<[^>]*>)|\$(?=\d)", lambda m: m[1] or "$\u2060", t)  # skip tags/URLs

def plain(t):
    return re.sub(r"\s+", " ", re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t).replace("*", "")).strip()

def caption(paras, limit=200):
    # hook = first sentence(s) of the cold open, plain text, cut at a word boundary, ending in "..."
    s = plain(paras[0]) if paras else ""
    s = re.split(r"(?<=[.!?])\s", s)[0].rstrip(".!? ")
    if len(s) > limit: s = s[:limit].rsplit(" ", 1)[0].rstrip(",;: ")
    return s + "..."

def main():
    if len(sys.argv) != 2: sys.exit("usage: ./run.sh x-article <edition>")
    ed = sys.argv[1]; src = f"{ROOT}/reports/{ed}.md"
    if not os.path.exists(src): sys.exit(f"missing {src}")
    text = open(src, encoding="utf-8").read()
    fm = {}
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if m:
        for line in m[1].splitlines():
            k, _, v = line.partition(":"); fm[k.strip()] = v.strip().strip('"')
        text = text[m.end():]
    lines = [l for l in text.splitlines() if "mind blow" not in l.lower()]
    paras = [p.strip() for p in re.split(r"\n\s*\n", "\n".join(lines)) if p.strip()]
    title = fm.get("title", ed); dek = fm.get("dek", "")
    if "mind blow" in title.lower(): sys.exit("title contains 'Mind Blow': fix the article first")
    if "mind blow" in dek.lower(): dek = ""
    body = [f"<p>{inline(p)}</p>" for p in paras]  # dek omitted: X auto-links it oddly and it repeats the cold open
    os.makedirs(OUT, exist_ok=True); out = f"{OUT}/{ed}.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(f'<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(title)}</title></head>\n'
                f'<body><div id="article">\n' + "\n".join(body) + "\n</div></body></html>\n")
    print(f"TITLE: {title}\nCAPTION: {caption(paras)}\n  (suggestion: rewrite to name the biggest concrete topic with numbers; keep the trailing ...)")
    print(f"HTML: {out} ({len(paras)} paragraphs)")
    print(f"SERVE: python3 -m http.server {PORT} --bind 127.0.0.1 -d {OUT}  ->  http://127.0.0.1:{PORT}/{ed}.html")

if __name__ == "__main__": main()
