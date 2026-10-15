#!/usr/bin/env python3
"""Followed-account sources for the X search.

Usage: x_accounts.py [queries|list]
  queries (default): print one search_posts_all query per line, handles from config/x_accounts.txt OR'd as
                     from:handle in batches kept under ~220 chars (~11 handles) (the routine appends the BASE suffix)
  list:              print the handles
x_filter.py imports load() to give these authors the relaxed "followed" route.
"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = f"{ROOT}/config/x_accounts.txt"
MAX_CHARS = 220  # ~11 handles: 25 results per call, so small batches keep prolific accounts from crowding out the rest
def load(path=PATH):
    try: lines = open(path, encoding="utf-8").read().splitlines()
    except FileNotFoundError: return []
    out = []
    for ln in lines:
        h = ln.split("#", 1)[0].strip().lstrip("@")
        if h and re.fullmatch(r"\w{1,15}", h) and h.lower() not in {x.lower() for x in out}: out.append(h)
    return out
def queries(handles):
    batches, cur = [], []
    for h in handles:
        if cur and len(" OR ".join(f"from:{x}" for x in cur + [h])) + 2 > MAX_CHARS: batches.append(cur); cur = []
        cur.append(h)
    if cur: batches.append(cur)
    return ["(" + " OR ".join(f"from:{x}" for x in b) + ")" for b in batches]
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "queries"
    hs = load()
    print("\n".join(hs if mode == "list" else queries(hs)))
