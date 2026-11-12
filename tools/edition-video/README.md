# Edition video

Turns one published edition into a silent, voiceover-ready 1920x1080 30 fps MP4 (about 5-8
minutes) plus a teleprompter with segment timecodes and a `post-attribution.md` credits file
to paste into the video's post. Anthony records his own voiceover over the picture, and films
the cold open and the sign-off himself.

All heavy work (yt-dlp, Chromium captures, ffmpeg) runs on the render host from `config/whisper.json`
(`remote`), never on the box. The box only edits `script.md`, looks up X posts and handles, and
copies files over SSH.

## Rebuild for another edition

1. Write `/workspace/edition-video/<EDITION>/script.md` from `reports/<EDITION>.md` (format below;
   aim for 700-1,100 narration words, short playful sentences, one beat per item). Keep a Cold open
   and a Sign-off in the script so they show up in the teleprompter; do not add visuals for them.
   The video starts at the first story and ends after the last one. The first story's clock is 00:00.0.
2. Find 3-6 related X posts per story so the segment can show how big the story is. Search with
   the x-namespace tools (high-engagement, on-topic posts from credible accounts; skip spam and
   NSFW). Either add `xpost` lines to the script, or write `xposts.json` next to it (see Auto X posts).
   `tools/edition-video/auto_xposts.py queries script.md` prints a suggested search query per segment.
3. Confirm X handles for every YouTube channel, news outlet, company or person the video uses, and
   write them to `handles.json` (see Credits). Never guess a handle.
4. Run `tools/edition-video/remote.sh <EDITION>`. It copies the tools to `~/Projects/edition-video/bin/`
   on the host, builds in `~/Projects/edition-video/<EDITION>/`, and copies `final.mp4`,
   `teleprompter.md`, `timeline.json`, `report.json`, `post-attribution.md` and `attribution.json`
   back to `/workspace/edition-video/<EDITION>/`.
5. Check `report.json` for failed sources, substitutions, chosen X post URLs, and any unresolved
   handles, then hand over the MP4, the teleprompter, and `post-attribution.md`.

On the host directly: `~/Projects/edition-video/bin/build.sh <EDITION>`. Downloads and captures are
cached under `cache/` (cache keys include the color theme), so edit the script and re-run to retime
cheaply. To render one segment only: `build.sh <EDITION> --segment 09`.

## script.md format

```
Edition: https://anthonyrussano.github.io/youtube-digest/reports/<EDITION>.html
## 01 Cold open
Camera: self
Narration: One paragraph that gets read aloud on camera.
## 02 First story
Narration: One paragraph that gets read aloud.
Visuals:
- yt https://www.youtube.com/watch?v=ID @SECONDS | Lower-third label
- page https://example.com/article | Site name | Fallback card title
- xpost https://x.com/handle/status/ID | @handle
- card Big title | small subtitle
## 13 Sign-off
Camera: self
Narration: Goodbye on camera.
```

- Each *video* segment lasts `words / 2.5 + 0.7` seconds and is cut into ~3 s shots that cycle
  through its visuals. On-camera sections are not in the MP4.
- Segments titled Cold open, Sign-off, or Outro are on camera by default. So is any segment with
  `Camera: self` (or `Visuals: on camera`). Use `Camera: video` or `--include-open-close` only if
  you really want those sections in the file.
- `yt`: downloads only `SECONDS-1 .. SECONDS+14` (<=1080p, no cookies, muted), then punch-in zooms.
- `page`: headless Chromium capture in dark mode, shown as slow scrolls and punch-ins. Blocked or
  blank pages become a title card; failed YouTube clips use the thumbnail.
- `xpost`: a real dark-mode screenshot of that post. The public embed
  (`https://platform.twitter.com/embed/Tweet.html?id=ID&theme=dark`) is tried first; if it does not
  render logged out, the build falls back to a dark card painted from X's public oEmbed. A `page`
  line that points at an x.com/twitter.com status URL is treated the same way.
- `card`: a generated headline card (dark theme by default). Use this for paywalled pages; keep
  these when the live page cannot be captured.
- `edition`: the GitHub Pages edition page. **Not used** unless you pass `--include-edition`. The
  edition headline is often about a different story, which is confusing mid-segment.
- Output has a silent AAC track so editors see an audio lane. No narration text is burned in.

## Dark mode

Captures default to dark mode: Playwright `colorScheme: 'dark'`, plus Chromium force-dark
(`--enable-features=WebContentsForceDark` and `--blink-settings=forceDarkModeEnabled=true`) so
sites without a native dark theme still come back dark. Headline cards use a dark theme too. Turn
this off with `--no-dark` on `build.sh` / `remote.sh`, or `EV_DARK=0`.

## Auto X posts

`xposts.json` next to `script.md` is merged into each video segment, up to 6 posts, skipping
duplicates already listed as `xpost` lines:

```
{
  "09": [
    {"url": "https://x.com/Reuters/status/123", "handle": "Reuters", "label": "Reuters"}
  ]
}
```

`auto_xposts.py pick script.md results.json -o xposts.json` will rank a dumped X search (see the
script's docstring for the shape) and pick about 3-6 posts per segment. Chosen post URLs are also
recorded in `report.json` under `xposts`.

## Credits (`post-attribution.md`)

Every build writes `post-attribution.md` next to `final.mp4`, grouped by segment in video order.
For every source the video uses it lists the X account of each person, company, publication or
YouTube creator involved — including the X posts shown, the YouTube channels clipped, and the news
outlets covered. Each account is written as `@handle (https://x.com/handle)`. Every shown X post
also gets a direct link to the post. Non-X URLs (YouTube, news sites, GitHub Pages) are left out.

Only handles that have been confirmed belong in this file. Put them in `handles.json`:

```
{
  "AI Engineer": "aiDotEngineer",
  "CBS News": "CBSNews",
  "The Wall Street Journal": "WSJ",
  "_entities": {
    "09": [
      {"entity": "Nvidia", "handle": "nvidia"},
      {"entity": "Jensen Huang", "handle": "JensenHuang"}
    ]
  }
}
```

Resolve handles with the x-namespace user lookup or search tools. If a channel, outlet or person
cannot be matched, it is listed under `unresolved` in `report.json` and omitted from the markdown.
Never guess. You can also generate or refresh the file without a render:

    python3 tools/edition-video/attribute.py /workspace/edition-video/<EDITION>
    python3 tools/edition-video/attribute.py /workspace/edition-video/<EDITION> --as-shot
