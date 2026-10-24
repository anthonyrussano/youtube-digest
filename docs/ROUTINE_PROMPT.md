# Edition routine prompt (paste into the scheduled Grok Bot routine)

Schedule (America/Los_Angeles): weekdays cron `4 6,12,17 * * 1-5` (6:04 AM, 12:04 PM, 5:04 PM PT; the 6:04 Article is held to 10:37 AM) and weekends cron `4 12,17 * * 0,6` (Saturday and Sunday 12:04 PM and 5:04 PM PT; each Article posts immediately), plus on demand. **Weekdays also run the overnight prep at ~12:30 AM PT** (`docs/OVERNIGHT.md`); when `articles/x/<today>/overnight.json` exists with status ready or partial, the 6:04 AM run follows `docs/OVERNIGHT.md` section 2 instead of starting from scratch. Every Article post keeps a 2-hour gap from the previous one and none posts after 9 PM PT (step 8e timing gate). The same prompt works for every edition; each routine adds a short preface. The full set of routines (weekday and weekend editions, the 10:37 weekday morning X post, the impressions tracker) with their prefaces is in `docs/HANDOFF.md` section 3.

```
Run one edition of Anthony's AI & DevOps digest (internal format name "Mind Blow"; never write that phrase in titles,
bodies or captions). Repo: /home/box/youtube-digest
(GitHub anthonyrussano/youtube-digest, site https://anthonyrussano.github.io/youtube-digest/).
First read README.md (especially "Editions"), STYLE.md (website edition, always the roundup) and
docs/X_ARTICLE_STYLE.md (the two X Article formats, how to pick one, the four steps for both) in full. They are the spec. Never commit
subscriptions.csv, data/, state/, cookies or any secret, and never print the subscription list anywhere public.

OVERNIGHT CHECK (weekday 6:04 AM run): if articles/x/<today PT date>/overnight.json exists with "status" ready or
   partial, follow docs/OVERNIGHT.md section 2 (no new edition-start; collect only after its window_end; fold big
   new items in briefly, don't redo research; publish from its draft-report.md; leave the Article for 10:37; report
   what overnight.json flagged). Missing or "failed": run all steps below as normal.
0. cd /home/box/youtube-digest && ./run.sh edition-start
   Note EDITION (page id) and START (ISO UTC window start = previous edition's publish time, else now-24h).
1. ./run.sh fetch          (yt-dlp channel listing; only new videos since START; exact dates for keyword matches)
2. JUDGE: read data/videos.json, skipping Shorts. (Seen/published videos are already excluded; a skipped
   edition marks nothing seen, so its videos come back next time.) Write data/selected.json as
   {"<video_id>": "AI" | "DevOps"} with only videos genuinely about AI/ML or DevOps, infra, homelab,
   networking, security or databases (README "Relevance criteria"). Write {} if none. Relevance first;
   when trimming borderline picks, keep those matching a top trend category from yesterday's/today's
   data/x_trends.json (if present).
2b. ./run.sh feeds        (RSS/Atom feeds in config/feeds.txt since START -> data/feeds.json; seen/published
   articles already excluded; shortlisted items carry full text, capped ~6k chars, else the RSS summary)
   FEEDS JUDGE: read the shortlisted items in data/feeds.json ("items_list", "shortlisted": true; others only by
   title) and pick 3-6 articles that are genuinely about AI/ML or DevOps (same criteria as videos), using only
   their "text". Prefer tier-1 primary sources (official blogs, release notes, advisories) over news and
   aggregators. A story also covered by a video and/or an X post appears ONCE as one merged item, cited to the
   primary blog/article URL (the video/X links may support details in the same item). Write the picks to
   data/feeds_selected.json as {"<item id>": "AI" | "DevOps"} ({} if none).
2c. ./run.sh ainews       (the daily AINews email issue(s) since START -> data/ainews.json, via the box-private,
   read-only mail bridge; if it prints "mail bridge unavailable", carry on without it and note it in the report)
   AINEWS JUDGE: read data/ainews.json "items_list" (title, summary, sources, primary_url; "theme" groups bullets
   of one story) and pick the stories genuinely about AI/ML or DevOps that are big, concrete and new (usually 3-8).
   Write data/ainews_selected.json as {"<item id>": "AI" | "DevOps"} ({} if none). Use only facts in the item's
   summary. Link the claim to the item's original sources (prefer primary_url: the X post, paper, repo or blog),
   NEVER to the newsletter, substack, latent.space or the email, and never say "AINews" or "newsletter".
   Group: one story covered by AINews and by a feed article, X post or video is ONE item, cited to the primary
   source (and merge several AINews bullets with the same "theme" into one item).
3. ./run.sh transcripts    (429s get status "rate limited (retry later)"; at publish they go to state/retry.json and are
   retried by the next editions, so this is fine; retry-queue videos have "retry": true in data/videos.json)
3b. ./run.sh whisper       (Whisper fallback for "needs Whisper" videos only. Backend order: remote GPU host if
   WHISPER_REMOTE is set and reachable (whisper.cpp large-v3-turbo on Vulkan via ssh + docker, videos up to 3 h),
   else or on any remote failure local CPU faster-whisper base.en int8. Local skips videos over 45 min, caps each at 20 min wall time and 1.5 GB RSS, deletes audio. Transcripts land in data/transcripts/
   with status "ok" like captions. Failures are non-fatal: those videos go to "Also on the radar". Never set
   WHISPER_REMOTE yourself. 429 videos that failed 2+ editions are sent to Whisper automatically.)
   Remote yt-dlp: YouTube bot-blocks this box, so fetch/transcripts/whisper run every yt-dlp call on the home GPU host
   over ssh ("ytdlp_remote" in config/whisper.json); on the remote backend audio is downloaded and converted there.
   Each step prints "yt-dlp: running on remote host"; if it prints "REMOTE HOST UNREACHABLE ... falling back", expect
   bot-check failures, say so in the report, and don't probe the host with nc or /dev/tcp. Never use YouTube cookies.
4. X: first trends, then searches. Pace every X call at <= 25 per minute (wait ~60 s between batches of 25).
   4a. TRENDS (once per PT day): ./run.sh trends. If it prints CACHED, spend no reads. Otherwise it prints one
   JSON line per category: call MCP "x" tool get_posts_counts_recent with that line's "args" (write_to_file=true)
   and copy each result to data/x_counts/<name>.json (about 27 reads), then ./run.sh trends compute
   -> data/x_trends.json ("top" = up to 5 categories whose volume today is >= 1.1x the 7-day average).
   4b. SEARCH: ./run.sh x-reset. For EVERY non-comment line Q in config/x_queries.txt, call MCP namespace "x",
   tool search_posts_all, with
   {"query": "Q -is:retweet -is:reply lang:en", "max_results": 25, "sort_order": "relevancy",
    "start_time": START, "post.fields": "public_metrics,created_at,author_id",
    "expansions": "author_id", "user.fields": "username,name"} and write_to_file=true.
   Copy each result file to data/x_raw/qNN.json (33 calls: topics, launches and curated accounts).
   Then run ./run.sh x-accounts and make the same call for EVERY line it prints (followed accounts from
   config/x_accounts.txt, 3 calls), copying each result to data/x_raw/aNN.json. Posts by these authors get a
   relaxed "followed" route in x_filter.py (>= 5 bookmarks, bookmarks >= 0.1x likes, saves or >= 10 reposts
   or >= 3 quotes).
   Then: ./run.sh x   -> data/x_selected.json (posts matching a top trend carry "trends" and rank 1.5x higher)
   Budget: <= ~55 search reads per edition (36 today) plus <= 30 trend reads once a day (limits 30/min, 1000/day).
5. DECIDE: if no new video has transcript_status "ok" in data/relevant.json AND fewer than 5 good X items
   qualify AND fewer than 2 strong articles (tier 1-2, in data/feeds_selected.json) qualify, stop and publish nothing (report "skipped: nothing new"). AINews stories never count toward this rule (render ignores X posts found only via AINews). Otherwise write articles/<EDITION>.md
   exactly per STYLE.md (Mind Blow format), using only the new transcripts (data/transcripts/<id>.txt),
   data/x_selected.json, the articles in data/feeds_selected.json and the stories in data/ainews_selected.json (link the article or original source URL on the claim;
   write article items exactly like video items, no "according to a blog post" framing). Write X items exactly like video items, with no platform framing or counts.
   TRENDS: favor stories in data/x_trends.json "top" categories (videos in step 2 and X posts alike, given
   equal quality): lead the cold open with the strongest trending story. The X share caption (STYLE.md "X share caption")
   leads with the single most useful, actionable takeaway for developers/DevOps (a how-to, pattern or tip,
   preferably about agent/coding tools like Claude Code, Cursor, Codex), never with spec numbers or model sizes. Never mention trends or volumes in the article.
   Use only facts from the transcripts and posts, and never repeat stories from earlier editions.
6. Run through the STYLE.md pre-publish checklist, then ./run.sh render. Fix any missing-citation or
   reuse error and re-run. If it prints SKIP:, publish nothing.
7. ./run.sh publish. Wait about 90 s, then confirm
   https://anthonyrussano.github.io/youtube-digest/reports/<EDITION>.html returns HTTP 200 and the index lists it.
8. X ARTICLE FORMAT (every run, weekday and weekend, including 6:04 AM). DEFAULT (since 2026-10-24): the CLASSIC
   FULL ROUNDUP of docs/X_ARTICLE_STYLE.md "Winning formula": article.md = the whole edition (every story its own
   linked paragraph, 10+ paragraphs, 1,000+ words, no ## sections, no bulleted Also list), title = three named
   items with numbers (<=100 chars), tip-first caption ending "...", 1-3 [[IMG]] lines incl. >=1 cited video frame.
   format.txt line 1 "roundup". The text below (four steps, lead-first roundup, deep-dive) applies only when
   Anthony asks for a deep dive. Older rule, kept for reference: pick "roundup" or "deep-dive" per
   docs/X_ARTICLE_STYLE.md "Selection rule". Deep-dive only if the edition has ONE lead story with a genuinely
   overlooked angle, an actionable takeaway and enough primary-source material for ~400-600 words; otherwise
   roundup (always for thin editions with no strong lead). If both fit, alternate: look at the "format" of the
   last posted Article in state/x_posts.json and pick the other one. Write articles/x/<EDITION>/format.txt:
   line 1 the format, line 2 a one-line reason (public text only), line 3 (roundup) "caption: ..." (same caption
   as article.md front matter).
   BOTH FORMATS go through the same four steps, saving all four artifacts under articles/x/<EDITION>/ in order.
   (The website edition reports/<EDITION>.md stays the classic roundup per STYLE.md; it is no longer the X
   Article source.) A ROUNDUP Article still covers several stories, one short paragraph per story, but it LEADS
   with one item: its overlooked angle, researched and explained in plain language, then the other items, then a
   closing question or call to action.
   8a. research.md: raw facts from the cited sources (transcripts, articles, full X threads, AINews items via their
       original sources) + a quick web/X search for what most creators covered and what they overlooked or
       under-explained. Confirm the lead: the most overlooked or most practical story, preferably an actionable
       dev/DevOps/agent-tooling idea. Prioritize overlooked technical details, implications and nuances.
       Deep-dive: if the research shows the angle is not really overlooked or the material is thin, switch to
       roundup (update format.txt) and continue with 8b-8d as a roundup. Roundup: pick the lead item here (its
       overlooked angle) and note the facts for the other items.
   8b. outline.md: one core idea at a time, plain language, jargon dropped or defined at once, why it matters and
       what people are missing. Deep-dive: plus 4-6 "Also this cycle" picks. Roundup: the lead item's angle in
       a few plain points, then the order of the other items (one line each), then the closing question/CTA.
   8c. article.md: front matter title, caption (one actionable dev/DevOps tip first, ends in "...", no
       "$<number>", never "Mind Blow"), edition, lead_source. Short direct sentences.
       Deep-dive: title names the lead idea (not three stories); hook on the overlooked angle; ~400-800 words for
       the lead; takeaway, then a question or call to action; then "## Also this cycle" with 4-6 linked one-liners.
       Roundup: title leads with the lead item's idea (may tease 1-2 more); opens with the lead item's overlooked
       angle in plain language (a few short paragraphs); then one short linked paragraph per other story (same
       facts and sourcing as STYLE.md, no repeats from earlier editions); ends with a closing question or call to
       action that invites replies.
       Images (both formats, regular and overnight runs): each on its own line as [[IMG: /workspace/<file> | alt]].
       Types: video-frame, chart, diagram, page screenshot, licensed source figure (docs/OVERNIGHT.md 3/3b). If the
       Article cites a video, include at least 1 video frame when a frame shows a slide, demo, diagram, chart or
       code (never a talking head): ./run.sh yt-frame <video_id> <seconds> /workspace/<EDITION>-<n>-<slug>.png at
       the SAME timestamp the Article cites; alt names the channel and video; the text near it links the
       timestamped video; 1-2 frames per video, credited, for commentary (fair use). Record each in check.md (and
       overnight.json images on overnight runs) as kind "video-frame" with source_url and timestamp.
   8d. check.md: review research, tighten outline, check clarity, confirm the overlooked angle is real, sourced and
       explained simply; check title, caption (tip-first, "..."), no "$<number>", no "Mind Blow"; fix article.md if
       anything fails and record what changed.
   Either way: ./run.sh x-article <EDITION> must print the chosen FORMAT and SOURCE articles/x/<EDITION>/article.md
   (for both formats; "SOURCE: reports/<EDITION>.md" plus a NOTE means article.md is missing: go back to 8c).
   Commit articles/x/<EDITION>/ by that path
   (git add -- articles/x/<EDITION>; git commit -- articles/x/<EDITION>; pull --rebase, push).
8e. X ARTICLE POST (skip only on the weekday 6:04 AM run: the 10:37 routine posts it; every other run, including
   both weekend runs, posts right after publish, subject to the TIMING GATE below). Follow docs/HANDOFF.md "X Article
   playbook" exactly: localhost http server, copy via right-click menu, paste with real keystrokes, verify the
   body, new NASA header not in state/x_posts.json, the caption (article.md front matter; roundup may fall back to
   format.txt line 3), read the live caption back, append the post to state/x_posts.json WITH
   "format": "roundup" | "deep-dive".
   TIMING GATE (check right before posting; docs/HANDOFF.md "Article timing"). HARD RULE (2026-10-24, overrides the
   2-hour/9 PM items below): at most 2 Articles per PT day, >= 4 h apart, only 8:00 AM-3:00 PM PT; otherwise HOLD
   for the next valid slot and report it (so a 17:04 run's Article is held for the next day).
   - 2-HOUR GAP: read the latest posted_at_utc in state/x_posts.json. If it is less than 2 hours ago, do NOT
     post now. The Article stays committed under articles/x/<EDITION>/; hold it for the next slot that is at least
     2 h after that last post, and put "X Article HELD: <EDITION>, next slot <h:mm AM/PM PT> (last post <h:mm PT>)"
     in the run report so the parent can queue it.
   - NO POSTS AFTER 9 PM PT: if it is after 9:00 PM PT (e.g. a late-night on-demand deep dive), do not post;
     hold it for the next 12:04 PM PT slot (still at least 2 h after the last post) and report it the same way.
     The only exception is Anthony explicitly saying "post now" for that Article.
   - Weekday morning: the 6:04 AM edition's Article posts at 10:37. If Anthony asked for it early and it is already
     in state/x_posts.json, the 10:37 routine skips it. Either way the 12:04 run's Article must still be >= 2 h
     after that post (a 10:37 post means no 12:04 Article before 12:37 PM PT).
9. MESSAGE Anthony (not between 10 PM and 5:30 AM PT): headline, link (X post, else the Pages URL) and one
   sentence on the top item. Never message anyone else without his confirmation.
Report: EDITION, the window, feeds ok/items/shortlisted/articles cited, AINews issues/items/stories cited (or bridge error), videos found/selected/transcribed (captions vs Whisper)/rate limited, X calls (search + trend reads) and posts qualified (saves vs shares route), top trends,
the X Article format and why (roundup/deep-dive), its title and lead story, the live URL (or why it was skipped or HELD,
with the next slot in PT), and any errors.
```
