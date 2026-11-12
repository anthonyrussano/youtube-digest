# Edition video

The full process, rules, QA checklist and changelog live in
[`docs/EDITION_VIDEO.md`](../../docs/EDITION_VIDEO.md). This file is the short tool reference.

Turns one published edition into a voiceover-ready 1920x1080 30 fps MP4 (about 5-8 minutes)
plus a teleprompter with segment timecodes, a quiet music stem, and a `post-attribution.md`
credits file to paste into the video's post. Anthony records his own voiceover over the picture.
The video is voiceover only by default — cold open and sign-off are regular edited segments.

All heavy work (yt-dlp, Chromium captures, ffmpeg, music render) runs on the render host from
`config/whisper.json` (`remote`), never on the box. The box only edits `script.md`, looks up
X posts and handles, and copies files over SSH.

## Rebuild for another edition

1. Write `/workspace/edition-video/<EDITION>/script.md` from `reports/<EDITION>.md` (format below;
   aim for 700-1,100 narration words, short playful sentences, one beat per item, a cold open and
   a sign-off). The cold open is a teaser montage: one punchy shot or X post for each story it
   mentions, in that order, plus dark title cards where they help. Never show the GitHub Pages
   edition page. The outro is a clean dark end card.
2. Find 3-6 related X posts per newsy story so the segment can show how big it is. Search with
   the x-namespace tools (high-engagement, on-topic posts from credible accounts; skip spam and
   NSFW). Either add `xpost` lines to the script, or write `xposts.json` next to it (see Auto X posts).
   `tools/edition-video/auto_xposts.py queries script.md` prints a suggested search query per segment.
3. Confirm X handles for every YouTube channel, news outlet, company or person the video uses, and
   write them to `handles.json` (see Credits). Never guess a handle.
4. Run `tools/edition-video/remote.sh <EDITION>`. It copies the tools to `~/Projects/edition-video/bin/`
   on the host, builds in `~/Projects/edition-video/<EDITION>/`, and copies `final.mp4`,
   `teleprompter.md`, `timeline.json`, `report.json`, `post-attribution.md`, `attribution.json`,
   `music.wav`, `music.mp3` and `music-license.txt` back to `/workspace/edition-video/<EDITION>/`.
5. Check `report.json` for failed sources, substitutions, chosen X post URLs, unresolved handles,
   and the music license, then hand over the MP4, the teleprompter, the music stem, and the credits.

On the host directly: `~/Projects/edition-video/bin/build.sh <EDITION>`. Downloads and captures are
cached under `cache/` (cache keys include the color theme), so edit the script and re-run to retime
cheaply. To render one segment only: `build.sh <EDITION> --segment 09`. Other useful flags:
`--no-music`, `--no-dark`, `--on-camera-open-close`, `--include-edition`, `--output name.mp4`.

## script.md format

```
Edition: https://anthonyrussano.github.io/youtube-digest/reports/<EDITION>.html
## 01 Cold open
Style: montage
Narration: One paragraph that teases today's stories, in order.
Visuals:
- stat 225,000 | lines of tests
- yt https://www.youtube.com/watch?v=ID @SECONDS | Lower-third label
- xpost https://x.com/handle/status/ID | @handle
- card An airline banned AI agents.
## 02 First story
Narration: One paragraph that gets read aloud.
Visuals:
- yt https://www.youtube.com/watch?v=ID @SECONDS | Lower-third label
- page https://example.com/article | Site name | Fallback card title
- stat 9% → 59% | coverage on the newer code
## 13 Sign-off
Style: end
Narration: The playful goodbye.
Visuals:
- endcard That's the cycle. | Trim a skill. Check your spec.
- endcard See you tomorrow | anthonyrussano.github.io/youtube-digest
```

- Each video segment lasts `words / 2.5 + 0.7` seconds (about 150 words a minute, plus a short
  breath). Teleprompter timecodes follow that clock, starting at 00:00.0 with the cold open.
- Cold open / Sign-off / Outro are regular video segments. `Style: montage` (the default for a
  cold open) plays each visual once, in order, and does not cycle back. `Style: end` is the
  default for a sign-off: clean centered dark end cards. `Camera: self` or `--on-camera-open-close`
  is the opt-in if those sections should be left out of the MP4.
- Inside a segment, cuts are hard. Between segments, a short dip-to-black uses the breath at the
  end of the line. Stills and cards get a subtle Ken Burns push or pan. Shot kinds are scheduled
  so the same type does not run more than twice in a row when another type is available. A small
  chapter label fades on at the start of each story. Lower-thirds name the source or channel.
  A consistent dark grade, vignette and light grain sit on every shot.
- `yt`: downloads only `SECONDS-1 .. SECONDS+14` (<=1080p, no cookies, **muted**), then a punch-in
  or pan. Failed clips fall back to the thumbnail.
- `page`: headless Chromium capture in dark mode, shown as a slow scroll or punch-in. Blocked or
  blank pages become a title card.
- `xpost`: a real dark-mode screenshot of that post. The public embed
  (`https://platform.twitter.com/embed/Tweet.html?id=ID&theme=dark`) is tried first; if it does not
  render logged out, the build falls back to a dark card painted from X's public oEmbed. A `page`
  line that points at an x.com/twitter.com status URL is treated the same way.
- `card` / `stat` / `endcard`: generated dark headline, number, or sign-off cards, with consistent
  typography (Noto Sans, gold accent).
- `edition`: the GitHub Pages edition page. **Not used** unless you pass `--include-edition`. Never
  use this in a mid-story or in the cold open — the edition headline is often about a different
  story and reads as confusing.

## Music

A procedural lofi-synth / chillwave bed is generated on the host by `music.py` (warm low-passed
pad, electric-piano chords, soft bass, swung drum loop, light crackle). It is an original
composition with no third-party samples, dedicated to the public domain under **CC0 1.0**, and
safe for YouTube and X. The mix sits quietly at about **-22 LUFS** (in the -24 to -20 range)
under where the voiceover will go, with a fade in and fade out. The loop is 16 bars at 80 BPM
and tiles cleanly for a 5–8 minute video.

`music.wav` (24-bit, 48 kHz stereo) is written next to the MP4 as a stem you can adjust in an
editor. `music.mp3` (192 kbps) is the chat-sized copy (attachments must stay under 25 MB).
`music-license.txt` records the source and license. Cited YouTube clips stay muted.
Turn the bed off with `--no-music` or `EV_NO_MUSIC=1`.

## Dark mode

Captures default to dark mode: Playwright `colorScheme: 'dark'`, plus Chromium force-dark
(`--enable-features=WebContentsForceDark` and `--blink-settings=forceDarkModeEnabled=true`).
Article crops start at the headline. If a site is still light, the build inverts the PNG and
keeps photos, or frames the article on a dark card. Headline cards are dark too. Turn this
off with `--no-dark` on `build.sh` / `remote.sh`, or `EV_DARK=0`.

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
