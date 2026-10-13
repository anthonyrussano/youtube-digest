# Daily routine prompt (paste into the scheduled Grok Bot routine)

```
Run Anthony's daily AI & DevOps "Mind Blow" digest. Repo: /home/box/youtube-digest
(GitHub anthonyrussano/youtube-digest, site https://anthonyrussano.github.io/youtube-digest/).
First read README.md and STYLE.md in full. They are the spec. Never commit subscriptions.csv, data/, state/,
cookies or any secret, and never print the subscription list anywhere public.

1. cd /home/box/youtube-digest && ./run.sh rss --hours 24
2. JUDGE: read data/videos.json (skip Shorts and already-seen videos). Write data/selected.json as
   {"<video_id>": "AI" | "DevOps"}, including only videos that are genuinely about AI/ML or DevOps, infra,
   homelab, networking, security or databases (criteria in README "Relevance criteria").
3. ./run.sh transcripts   (429s get status "rate limited (retry later)" and are retried next run, which is fine)
4. X: ./run.sh x-reset. Compute START = now minus 24 h in ISO UTC (date -u -d '24 hours ago' +%FT%TZ).
   For EVERY non-comment line Q in config/x_queries.txt, call MCP namespace "x", tool search_posts_all, with
   {"query": "Q -is:retweet -is:reply lang:en", "max_results": 25, "sort_order": "relevancy",
    "start_time": START, "post.fields": "public_metrics,created_at,author_id",
    "expansions": "author_id", "user.fields": "username,name"} and write_to_file=true.
   Copy each result file to data/x_raw/qNN.json (about 24 calls; stay under 30 per minute).
   Then: ./run.sh x   -> data/x_selected.json
5. WRITE articles/$(TZ=America/Los_Angeles date +%F).md exactly per STYLE.md (Mind Blow format), using
   data/relevant.json + data/transcripts/<id>.txt (every "ok" video) and data/x_selected.json. Write X items
   exactly like video items, with no platform framing or counts. Use only facts from the transcripts and posts.
6. Run through the STYLE.md pre-publish checklist, then ./run.sh render (fix any missing-citation error and re-run).
7. ./run.sh publish. Wait about 90 s, then confirm
   https://anthonyrussano.github.io/youtube-digest/reports/<date>.html returns HTTP 200 and shows the new title.
If no relevant video has a transcript, skip steps 5–7 and publish nothing (the X posts alone don't make a report).
Report: videos found, selected, transcribed, rate limited; X calls and posts qualified; the live URL; any errors.
```
