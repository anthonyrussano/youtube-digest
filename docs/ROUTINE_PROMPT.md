# Edition routine prompt (paste into the scheduled Grok Bot routine)

Schedule: cron `4 6,12,17 * * 1-5` America/Los_Angeles (6:04 AM, 12:04 PM, 5:04 PM PT weekdays), plus on demand. The same prompt works for every edition. The full set of routines (including the 10:37 morning X post and the impressions tracker) is in `docs/HANDOFF.md`.

```
Run one edition of Anthony's AI & DevOps digest (internal format name "Mind Blow"; never write that phrase in titles,
bodies or captions). Repo: /home/box/youtube-digest
(GitHub anthonyrussano/youtube-digest, site https://anthonyrussano.github.io/youtube-digest/).
First read README.md (especially "Editions"), STYLE.md and docs/X_ARTICLE_STYLE.md in full. They are the spec. Never commit
subscriptions.csv, data/, state/, cookies or any secret, and never print the subscription list anywhere public.

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
8. X ARTICLE SOURCE (every run, including 6:04 AM): write the single-lead-story X Article for this edition per
   docs/X_ARTICLE_STYLE.md, saving all four artifacts under articles/x/<EDITION>/ and doing the steps in order:
   8a. research.md: raw facts from the cited sources (transcripts, articles, full X threads, AINews items via their
       original sources) + a quick web/X search for what most creators covered and what they overlooked or
       under-explained. Pick the lead: the most overlooked or most practical story, preferably an actionable
       dev/DevOps/agent-tooling idea. Prioritize overlooked technical details, implications and nuances.
   8b. outline.md: one core idea at a time, plain language, jargon dropped or defined at once, why it matters and
       what people are missing, plus 4-6 "Also this cycle" picks.
   8c. article.md: front matter title (names the lead idea, not three stories), caption (one actionable tip,
       ends in "...", no "$<number>", never "Mind Blow"); hook on the overlooked angle; short direct sentences;
       ~400-800 words for the lead; takeaway, then a question or call to action; then "## Also this cycle"
       with 4-6 linked one-liners.
   8d. check.md: review research, tighten outline, check clarity, confirm the overlooked angle is real, sourced and
       explained simply; fix article.md if anything fails. Then ./run.sh x-article <EDITION> must print
       SOURCE: articles/x/<EDITION>/article.md. Commit articles/x/<EDITION>/ (git add that path; pull --rebase, push).
8e. X ARTICLE POST (skip on the 6:04 AM run: the 10:37 routine posts it). Follow docs/HANDOFF.md "X Article
   playbook" exactly: localhost http server, copy via right-click menu, paste with real keystrokes, verify the
   body, new NASA header not in state/x_posts.json, the caption from article.md front matter, read the live
   caption back, append the post to state/x_posts.json.
9. MESSAGE Anthony (not between 10 PM and 5:30 AM PT): headline, link (X post, else the Pages URL) and one
   sentence on the top item. Never message anyone else without his confirmation.
Report: EDITION, the window, feeds ok/items/shortlisted/articles cited, AINews issues/items/stories cited (or bridge error), videos found/selected/transcribed (captions vs Whisper)/rate limited, X calls (search + trend reads) and posts qualified (saves vs shares route), top trends,
the X Article lead story and title (articles/x/<EDITION>/), the live URL (or why it was skipped), and any errors.
```
