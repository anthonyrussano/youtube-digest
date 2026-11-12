# Edition video

Turns one published edition into a silent, voiceover-ready 1920x1080 30 fps MP4 (5-8 minutes) plus a
teleprompter with segment timecodes. Anthony records his own voiceover over it.

All heavy work (yt-dlp, Chromium captures, ffmpeg) runs on the render host from `config/whisper.json`
(`remote`), never on the box. The box only edits `script.md` and copies files over SSH.

## Rebuild for another edition

1. Write `/workspace/edition-video/<EDITION>/script.md` from `reports/<EDITION>.md` (format below; aim for
   700-1,100 narration words, short playful sentences, cold open, one beat per item, sign-off).
2. Run `tools/edition-video/remote.sh <EDITION>`. It copies `build.py`/`build.sh` to
   `~/Projects/edition-video/bin/` on the host, builds in `~/Projects/edition-video/<EDITION>/`, and copies
   `final.mp4`, `teleprompter.md`, `timeline.json` and `report.json` back to `/workspace/edition-video/<EDITION>/`.
3. Check `report.json` for failed sources and what replaced them, then hand over the MP4 and teleprompter.

On the host directly: `~/Projects/edition-video/bin/build.sh <EDITION>`. Downloads and captures are cached
under `cache/`, so edit the script and re-run to retime cheaply.

## script.md format

```
Edition: https://anthonyrussano.github.io/youtube-digest/reports/<EDITION>.html
## 01 Cold open
Narration: One paragraph that gets read aloud.
Visuals:
- yt https://www.youtube.com/watch?v=ID @SECONDS | Lower-third label
- page https://example.com/article | Site name | Fallback card title
- edition | Today's edition
- card Big title | small subtitle
```

- Each segment lasts `words / 2.5 + 0.7` seconds and is cut into ~3 s shots that cycle through its visuals.
- `yt`: downloads only `SECONDS-1 .. SECONDS+14` (<=1080p, no cookies, muted), then punch-in zooms.
- `page`: headless Chromium full-page capture, shown as slow scrolls and punch-ins. X posts render through
  X's public oEmbed. Blocked or blank pages become a title card; failed YouTube clips use the thumbnail.
- Output has a silent AAC track so editors see an audio lane. No narration text is burned in.
