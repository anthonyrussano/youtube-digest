#!/usr/bin/env python3
"""./run.sh plain-lint <EDITION> [--all]: advisory Plain English check (adapted from SimpleEnglish / ASD-STE100).

Lints reports/<EDITION>.md (else articles/<EDITION>.md, else articles/x/<EDITION>/draft-report.md) and
articles/x/<EDITION>/article.md with the vendored scripts/ste_lint.py (MIT, AminBlg/SimpleEnglish) plus our
WRITING_GUIDE ban list. Front matter, [[IMG]] lines, link URLs and code are skipped.

Findings are split in two:
  REVIEW  : sentences over 25 words, slop/ban-list words, ", making"-style -ing clauses, perfect tense
            ("has been"), em-dashes, semicolons, e.g./i.e./etc. Fix these unless the source wording needs them.
  VOICE   : counted only (contractions, may/could/should, trailing if/when, check/verify rotation). Our voice
            (STYLE.md) allows these, so they are never reported line by line unless --all.
Warn-only: exit 0, except exit 2 on a HARD-RULE violation ("Mind Blow" anywhere, "$" + digit in a title or
caption), which publishing and posting must not ship."""
import os, re, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ste_lint  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEW = ("sentence_over_limit", "slop_word", "ing_clause", "perfect_tense", "em_dash", "semicolon", "latin_abbrev", "ban_word")
VOICE = ("contraction", "banned_modal", "trailing_condition", "synonym_rotation")
TECH_NOUNS = {"harness", "harnesses"}
# docs/WRITING_GUIDE.md section 1 ban list (hype, filler, AI-tell) on top of slop.tsv
BAN = re.compile(r"\b(revolutionary|game.?chang\w*|groundbreaking|mind.?blowing|insane|unprecedented|cutting.edge|"
                 r"next.level|massive|huge|basically|essentially|incredibly|literally|it's worth noting|"
                 r"it's important to note|in today's world|needless to say|in order to|leverag\w*|seamless\w*|"
                 r"robust|delve\w*|unlock\w*|empower\w*|supercharg\w*|harness the power)\b", re.I)


def prep(text):
    """Blank front matter and [[IMG]] lines (keep line numbers), turn [text](url) into text."""
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), 0)
        for i in range(end + 1):
            lines[i] = ""
    lines = ["" if l.strip().startswith("[[IMG") else l for l in lines]
    body = "\n".join(lines)
    body = re.sub(r"\[([^\]]+)\]\((?:[^()]|\([^)]*\))*\)", r"\1", body)
    return body


def front(text, key):
    m = re.search(rf'^{key}:\s*"?(.*?)"?\s*$', text.split("\n---", 1)[0], re.M)
    return m[1] if m else ""


def check(path, show_all):
    text = open(path, encoding="utf-8").read()
    hard = []
    if re.search(r"mind\s*blow", text, re.I):
        hard.append('"Mind Blow" appears in the text')
    for k in ("title", "caption"):
        if re.search(r"\$\s?\d", front(text, k)):
            hard.append(f'"$" followed by a digit in {k}')
    body = prep(text)
    hits = ste_lint.lint_detail(body, "descriptive")
    # Technical nouns in our field that slop.tsv lists as verbs/metaphors ("agent harness", "eval harness").
    hits = [h for h in hits if not (h["category"] == "slop_word" and h["text"].lower() in TECH_NOUNS)]
    clean = ste_lint.strip_code(body)
    for m in BAN.finditer(clean):
        if not any(h["category"] == "slop_word" and h["line"] == clean.count("\n", 0, m.start()) + 1 and h["text"].lower() == m[0].lower() for h in hits):
            hits.append({"category": "ban_word", "text": m[0], "line": clean.count("\n", 0, m.start()) + 1})
    stats = ste_lint.lint(body, "descriptive")
    counts = Counter(h["category"] for h in hits)
    rel = os.path.relpath(path, ROOT)
    print(f"\n== {rel}: {stats['words']} words, {stats['sentences']} sentences, mean {stats['mean_sentence_words']}, longest {stats['longest_sentence_words']}")
    print("   REVIEW " + ", ".join(f"{c} {counts[c]}" for c in REVIEW if counts[c]) or "   REVIEW none")
    print("   VOICE (allowed, counted only) " + ", ".join(f"{c} {counts[c]}" for c in VOICE if counts[c]))
    for h in sorted(hits, key=lambda h: h["line"]):
        if h["category"] in REVIEW or show_all:
            print(f"   L{h['line']:<4} {h['category']:20} {h['text']}")
    for h in hard:
        print(f"   HARD-RULE: {h}")
    return bool(hard)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    show_all = "--all" in sys.argv
    if len(args) != 1:
        sys.exit("usage: ./run.sh plain-lint <EDITION> [--all]")
    ed = args[0]
    files = []
    for cand in (f"reports/{ed}.md", f"articles/{ed}.md", f"articles/x/{ed}/draft-report.md"):
        if os.path.exists(os.path.join(ROOT, cand)):
            files.append(cand); break
    if os.path.exists(os.path.join(ROOT, f"articles/x/{ed}/article.md")):
        files.append(f"articles/x/{ed}/article.md")
    if not files:
        sys.exit(f"plain-lint: nothing to lint for {ed}")
    hard = [check(os.path.join(ROOT, f), show_all) for f in files]
    print("\nAdvisory only (docs/WRITING_GUIDE.md \"Plain English rules\"): fix REVIEW hits that are real; quotes, names and"
          " source wording stay as they are.")
    if any(hard):
        print("HARD-RULE violation: fix before publish/post.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
