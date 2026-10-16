#!/usr/bin/env python3
"""AINews newsletter stage (./run.sh ainews): newest [AINews] issue(s) in the edition window -> data/ainews.json.

  ainews.py [--since ISO] [--hours H] [--latest N] [--out FILE] [--no-resolve] [--timeout 10]

* Mail comes from the private mail bridge on this box (/home/box/mail-bridge, env ~/.config/mail-bridge/env.sh,
  Vault AppRole). Strictly read-only: the folder is SELECTed read-only and bodies are fetched with BODY.PEEK[],
  so nothing is marked read and no flags/folders change. Only messages From swyx+ainews@substack.com with
  "[AINews]" in the subject are fetched. Nothing is ever sent.
* Window: --since, else state/current_edition.json start_utc (same as feeds/fetch), else --hours (default 24),
  matched on the email Date. --latest N ignores the window and takes the N newest issues (testing).
* Parses each issue into stories: the lead (title story), every bold story heading + bullet list in the
  "AI Twitter Recap", and every top-level item in the Reddit recaps. Each story gets a title, a summary and
  the source URLs it cites. substack.com/redirect links are unwrapped (one GET without the personal ?j= token,
  Location header only) and cached in data/ainews_cache/redirects.json; t.co/bit.ly-style hops are followed too.
  Primary sources (X posts, papers, GitHub, HF, official blogs) rank first; substack/latent.space/image links
  are dropped, so items never point at the email.
* Dedup: issues whose Message-ID is in state/ainews_seen.json "issues" are skipped; URLs in ainews_seen "urls",
  feeds_seen.json, published.json "articles" and X ids in published.json "x" are removed from stories (a story
  with no fresh source left is dropped). Never writes state/: `edition.py published` marks everything in
  data/ainews.json seen, so a skipped edition keeps its items.
* Fails softly: if the bridge/Vault is unreachable it writes {"ok": false, "error": ...} and exits 0.
"""
import argparse, concurrent.futures as cf, email, email.policy, email.utils, hashlib, html, json, os, re, sys, time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from feeds_canon import canon
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIDGE = os.environ.get("AINEWS_BRIDGE", "/home/box/mail-bridge/examples")
SENDER, TAG = "swyx+ainews@substack.com", "[AINews]"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
SHORTENERS = {"t.co", "bit.ly", "buff.ly", "lnkd.in", "ow.ly", "tinyurl.com", "dlvr.it", "substack.com", "email.mg.substack.com"}
DROP_HOST = re.compile(r"(^|\.)(substack\.com|latent\.space|substackcdn\.com|substack-post-media\.s3\.amazonaws\.com)$|^preview\.redd\.it$|^i\.redd\.it$")
def load(p, d):
    try: return json.load(open(p))
    except Exception: return d
def save(p, o): os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(o, open(p, "w"), indent=1)
def h(s): return hashlib.sha1(s.encode()).hexdigest()[:16]
def norm_ws(t): return re.sub(r"\s+", " ", html.unescape(t or "")).strip()

# ---------- mail (read-only) ----------
def fetch_issues(cutoff, latest):
    sys.path.insert(0, BRIDGE); import agent_mail as am
    user, pw = am.credentials()
    out = []
    with am.imap_connect(user, pw) as im:
        im.select("INBOX", readonly=True)                       # read-only: no \Seen, no expunge
        since = (cutoff - timedelta(days=1)).strftime("%d-%b-%Y") if not latest else \
            (datetime.now(timezone.utc) - timedelta(days=14)).strftime("%d-%b-%Y")
        _, d = im.uid("search", None, "FROM", f'"{SENDER}"', "SUBJECT", f'"{TAG}"', "SINCE", since)
        uids = d[0].split()
        hdrs = []
        for uid in uids:
            _, m = im.uid("fetch", uid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE MESSAGE-ID)])")
            hd = email.message_from_bytes(m[0][1], policy=email.policy.default)
            if SENDER not in str(hd["From"]).lower() or TAG not in str(hd["Subject"]): continue
            dt = email.utils.parsedate_to_datetime(str(hd["Date"])).astimezone(timezone.utc)
            hdrs.append((dt, uid, hd))
        hdrs.sort(key=lambda x: x[0], reverse=True)
        pick = hdrs[:latest] if latest else [x for x in hdrs if x[0] >= cutoff]
        for dt, uid, hd in pick:
            _, m = im.uid("fetch", uid, "(BODY.PEEK[])")         # PEEK: does not set \Seen
            msg = email.message_from_bytes(m[0][1], policy=email.policy.default)
            body = msg.get_body(preferencelist=("html",))
            if not body: continue
            out.append({"message_id": str(hd["Message-ID"] or uid.decode()).strip(), "subject": norm_ws(str(hd["Subject"])),
                        "date_utc": dt.strftime("%Y-%m-%dT%H:%M:%SZ"), "html": body.get_content()})
    return out

# ---------- parsing ----------
def parse_issue(raw):
    import lxml.html
    doc = lxml.html.fromstring(raw)
    for bad in doc.xpath("//style|//script|//head"): bad.drop_tree()
    def links(el): return [a.get("href") for a in el.iter("a") if a.get("href", "").startswith("http")]
    def text(el): return norm_ws(el.text_content())
    blocks = [e for e in doc.iter("h1", "h2", "h3", "h4", "p", "ul", "ol", "div")
              if e.tag != "div" or "tweet" in (e.get("class") or "")]
    stories, section, lead, cur, in_lead = [], "lead", None, None, True
    def top(el):  # skip elements nested in an already-handled list
        p = el.getparent()
        while p is not None:
            if p.tag in ("ul", "ol", "li"): return False
            if p.tag == "div" and "tweet" in (p.get("class") or ""): return False
            p = p.getparent()
        return True
    for e in blocks:
        if not top(e): continue
        t = text(e)
        if e.tag in ("h1", "h2", "h3", "h4"):
            low = t.lower()
            if "twitter recap" in low: section, in_lead = "twitter", False; cur = None; continue
            if "reddit recap" in low or "subreddit recap" in low or low.startswith("/r/"): section, in_lead = "reddit", False; cur = None; continue
            if "discord" in low and "recap" in low: section, in_lead = "discord", False; cur = None; continue
            if "invite your friends" in low or "share" == low: break
            if section == "reddit": cur = None
            continue
        if in_lead:
            if t.startswith("AI News for "): continue
            if e.tag == "p" or e.tag == "div":
                lead = lead or {"section": "lead", "title": None, "paras": [], "links": []}
                if len(t) > 40: lead["paras"].append(t)
                lead["links"] += links(e)
            continue
        if section == "twitter":
            strong = e.xpath("./strong|./b")
            if e.tag == "p" and strong and len(norm_ws(strong[0].text_content())) >= len(t) - 2 and 8 < len(t) < 200:
                cur = {"section": "twitter", "title": t, "skip": t.lower().startswith("top tweets")}; continue
            if e.tag in ("ul", "ol") and cur is not None and not cur["skip"]:  # "Top tweets" repeats earlier stories
                # each top-level bullet is its own story ("Theme: Label"); a bare "Group:" bullet splits into its children
                def own(li): return norm_ws(" ".join(p.text_content() for p in li.xpath("./p|./span")) or li.text or "")
                def label(li):
                    b = li.xpath("./p/strong|./strong|./p/b"); return norm_ws(b[0].text_content()).rstrip(":") if b else ""
                def add(li):
                    lt = own(li); lb = label(li)
                    det = [own(x) for x in li.xpath(".//li") if own(x)]
                    stories.append({"section": "twitter", "title": f"{cur['title']}: {lb}" if lb else cur["title"],
                                    "theme": cur["title"], "paras": [lt] + det, "links": links(li)})
                for li in e.xpath("./li"):
                    lt = own(li)
                    if lt.endswith(":") and len(lt) < 80: [add(x) for x in li.xpath("./ul/li|./ol/li")]
                    else: add(li)
                cur["done"] = True
        elif section in ("reddit", "discord"):
            if e.tag in ("ul", "ol"):
                for li in e.xpath("./li"):
                    first = (li.xpath("./p") or [li])[0]; ft = text(first)
                    if not ft: continue
                    m = re.match(r"^(.{8,220}?)\s*\(Activity: ?[\d,]+\):?\s*(.*)$", ft)
                    title, summ = (m.group(1), m.group(2)) if m else (ft[:120], ft)
                    st = {"section": section, "title": title, "paras": [summ], "links": links(li)}
                    for sub in li.xpath(".//li")[:3]:
                        stt = text(sub)
                        if stt: st["paras"].append(stt)
                    stories.append(st)
    if lead and lead["paras"]: stories.insert(0, lead)
    return stories

# ---------- links ----------
def resolve(u, cache, timeout):
    if u in cache: return cache[u]
    cur = u
    for _ in range(5):
        s = urlsplit(cur); host = s.netloc.lower()
        if host not in SHORTENERS and not (host.endswith("substack.com") and "/redirect/" in s.path): break
        if "/redirect/" in s.path: cur = urlunsplit((s.scheme, s.netloc, s.path, "", ""))  # drop personal ?j= token
        try:
            req = urllib.request.Request(cur, method="GET", headers={"User-Agent": "Mozilla/5.0"})  # full browser UA gets a 200 interstitial
            class NR(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, *a, **k): return None
            op = urllib.request.build_opener(NR)
            try: r = op.open(req, timeout=timeout); loc = None; r.close()
            except urllib.error.HTTPError as e: loc = e.headers.get("Location")
            if not loc: break
            cur = urllib.parse.urljoin(cur, loc)
        except Exception: break
    if "/redirect/" not in cur: cache[u] = cur  # do not cache failures
    return cur
def clean_url(u):
    s = urlsplit(u); host = s.netloc.lower().removeprefix("www.").removeprefix("mobile.")
    q = [(k, v) for k, v in parse_qsl(s.query, keep_blank_values=True)
         if not re.match(r"^(utm_|ref_?src|ref$|s$|t$|si$|fbclid|gclid|mc_|img$|publication_id|post_id|isFreemail|r$|triedRedirect)", k, re.I)]
    if host in ("twitter.com", "x.com", "fxtwitter.com", "vxtwitter.com"):
        host, q = "x.com", []
    return canon(urlunsplit(("https", host, s.path.rstrip("/") or "/", urlencode(q), "")))
def kind(u):
    host = urlsplit(u).netloc
    if host == "x.com": return ("x", 0) if "/status/" in u else ("x-profile", 6)
    if re.search(r"arxiv\.org|openreview\.net|\.pdf$|papers\.|aclanthology", u): return ("paper", 1)
    if host in ("github.com", "gist.github.com"): return ("github", 1)
    if host == "huggingface.co": return ("huggingface", 1)
    if host in ("reddit.com", "old.reddit.com"): return ("reddit", 4)
    if host == "news.ycombinator.com": return ("hn", 4)
    if host in ("youtube.com", "youtu.be"): return ("video", 2)
    if re.search(r"(^|\.)(techcrunch|theverge|bloomberg|reuters|cnbc|wsj|nytimes|theinformation)\.com$", host): return ("news", 3)
    return ("web", 2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since"); ap.add_argument("--hours", type=float, default=24)
    ap.add_argument("--latest", type=int, default=0, help="ignore the window, take the N newest issues (testing)")
    ap.add_argument("--out", default=f"{ROOT}/data/ainews.json"); ap.add_argument("--timeout", type=float, default=10)
    ap.add_argument("--no-resolve", action="store_true"); ap.add_argument("--state", default=f"{ROOT}/state")
    a = ap.parse_args(); t0 = time.time(); now = datetime.now(timezone.utc)
    since = a.since or (None if "--hours" in sys.argv else load(f"{ROOT}/state/current_edition.json", {}).get("start_utc"))
    cutoff = datetime.fromisoformat(since.replace("Z", "+00:00")) if since else now - timedelta(hours=a.hours)
    base = {"run_at": now.isoformat(), "since_utc": cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"), "source": "AINews (swyx+ainews@substack.com)"}
    try:
        issues = fetch_issues(cutoff, a.latest)
    except BaseException as e:  # bridge down, VPN down, Vault error, SystemExit from the client: soft failure
        msg = f"{type(e).__name__}: {e}"[:300]
        save(a.out, {**base, "ok": False, "error": msg, "issues": [], "items": 0, "items_list": []})
        print(f"ainews: mail bridge unavailable ({msg}); wrote empty {os.path.relpath(a.out, ROOT)} (non-fatal)"); return
    st = a.state; aseen = load(f"{st}/ainews_seen.json", {"issues": [], "urls": []}); pub = load(f"{st}/published.json", {})
    seen_urls = set(aseen.get("urls", [])) | set(load(f"{st}/feeds_seen.json", [])) | {canon(u) for u in pub.get("articles", [])}
    pub_x = set(pub.get("x", []))
    cache_p = f"{ROOT}/data/ainews_cache/redirects.json"; cache = load(cache_p, {})
    items, rep, counts = [], [], {"issues_seen": 0, "stories_dup": 0, "links_seen": 0}
    for iss in issues:
        if iss["message_id"] in aseen.get("issues", []) and not a.latest: counts["issues_seen"] += 1; continue
        stories = parse_issue(iss["html"])
        allraw = sorted({u for s in stories for u in s["links"]})
        if not a.no_resolve:
            with cf.ThreadPoolExecutor(16) as ex: list(ex.map(lambda u: resolve(u, cache, a.timeout), allraw))
        n = 0
        for idx, s in enumerate(stories):
            srcs, dupe = [], set()
            for raw in s["links"]:
                u = clean_url(cache.get(raw, raw))
                if DROP_HOST.search(urlsplit(u).netloc) or u in dupe: continue
                dupe.add(u)
                k, rank = kind(u); xid = re.search(r"/status/(\d+)", u)
                if u in seen_urls or (xid and xid.group(1) in pub_x): counts["links_seen"] += 1; continue
                srcs.append({"url": u, "kind": k, "rank": rank})
            if not srcs: counts["stories_dup"] += 1; continue
            srcs.sort(key=lambda x: x["rank"])
            title = s["title"] or iss["subject"].replace(TAG, "").strip()
            summ = " ".join(s["paras"]); summ = summ if len(summ) < 2500 else summ[:2500].rsplit(" ", 1)[0] + " …"
            items.append({"id": h(iss["message_id"] + title), "issue": iss["subject"], "issue_date_utc": iss["date_utc"],
                          "section": s["section"], "theme": s.get("theme"), "order": idx, "title": title, "summary": summ,
                          "primary_url": srcs[0]["url"], "sources": [{k: v for k, v in x.items() if k != "rank"} for x in srcs]})
            n += 1
        rep.append({"subject": iss["subject"], "date_utc": iss["date_utc"], "message_id": iss["message_id"],
                    "stories_parsed": len(stories), "items": n})
    save(cache_p, cache)
    out = {**base, "ok": True, "issues": rep, "items": len(items), "skipped": counts,
           "elapsed_s": round(time.time() - t0, 1), "items_list": items}
    save(a.out, out)
    print(f"ainews: issues={len(rep)} items={len(items)} skipped={counts} elapsed={out['elapsed_s']}s -> {os.path.relpath(a.out, ROOT)}")
    for r in rep: print(f"  {r['date_utc']} {r['subject'][:90]} ({r['items']} items)")
if __name__ == "__main__": main()
