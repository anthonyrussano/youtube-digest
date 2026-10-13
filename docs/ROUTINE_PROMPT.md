# Edition routine prompt (paste into the scheduled Grok Bot routine)

Schedule: weekdays at about 6:04 AM, 12:00 PM and 5:00 PM PT, plus on demand. The same prompt works for every edition.

```
Run one edition of Anthony's AI & DevOps "Mind Blow" digest. Repo: /home/box/youtube-digest
(GitHub anthonyrussano/youtube-digest, site https://anthonyrussano.github.io/youtube-digest/).
First read README.md (especially "Editions") and STYLE.md in full. They are the spec. Never commit
subscriptions.csv, data/, state/, cookies or any secret, and never print the subscription list anywhere public.

0. cd /home/box/youtube-digest && ./run.sh edition-start
   Note EDITION (page id) and START (ISO UTC window start = previous edition's publish time, else now-24h).
1. ./run.sh rss            (only videos published since START; seen/published ones are flagged)
2. JUDGE: read data/videos.json, skipping Shorts and "seen": true. Write data/selected.json as
   {"<video_id>": "AI" | "DevOps"} with only videos genuinely about AI/ML or DevOps, infra, homelab,
   networking, security or databases (README "Relevance criteria"). Write {} if none.
3. ./run.sh transcripts    (429s get status "rate limited (retry later)" and are retried next edition, which is fine)
4. X: ./run.sh x-reset. For EVERY non-comment line Q in config/x_queries.txt, call MCP namespace "x",
   tool search_posts_all, with
   {"query": "Q -is:retweet -is:reply lang:en", "max_results": 25, "sort_order": "relevancy",
    "start_time": START, "post.fields": "public_metrics,created_at,author_id",
    "expansions": "author_id", "user.fields": "username,name"} and write_to_file=true.
   Copy each result file to data/x_raw/qNN.json (about 24 calls; stay under 30 per minute).
   Then: ./run.sh x   -> data/x_selected.json
5. DECIDE: if no new video has transcript_status "ok" in data/relevant.json AND fewer than 5 good X items
   qualify, stop and publish nothing (report "skipped: nothing new"). Otherwise write articles/<EDITION>.md
   exactly per STYLE.md (Mind Blow format), using only the new transcripts (data/transcripts/<id>.txt)
   and data/x_selected.json. Write X items exactly like video items, with no platform framing or counts.
   Use only facts from the transcripts and posts, and never repeat stories from earlier editions.
6. Run through the STYLE.md pre-publish checklist, then ./run.sh render. Fix any missing-citation or
   reuse error and re-run. If it prints SKIP:, publish nothing.
7. ./run.sh publish. Wait about 90 s, then confirm
   https://anthonyrussano.github.io/youtube-digest/reports/<EDITION>.html returns HTTP 200 and the index lists it.
Report: EDITION, the window, videos found/selected/transcribed/rate limited, X calls and posts qualified,
the live URL (or why it was skipped), and any errors.
```
