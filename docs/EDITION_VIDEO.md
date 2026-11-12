# Edition videos

This guide is enough to build a voiceover-ready video from one published edition. Read it before you write a script or run a render.

The internal style name is "Mind Blow" (in the vein of Vsauce2). Never write those words in the video, the teleprompter, a title, or a caption. They belong only in this internal guide.

## Creative intent

Anthony records the voiceover himself. The picture is a horizontal 16:9 video, 1920x1080 at 30 fps, about 5 to 8 minutes long. It is voiceover only. There is no on-camera host unless he opts in.

The script comes from the GitHub Pages edition, not the other way around. A cold open teases today's stories in order. Each story then gets its own segment. A short sign-off closes the video.

The tone is playful and sharp. Short sentences. One beat per fact. The picture should feel like a late-night explainer, not a slide deck and not a recording of a web page.

## Rules

- Do not show the GitHub Pages edition page. Not in the cold open, not in a story, not in the outro. The edition headline often belongs to a different story and looks confusing on screen.
- Use dark mode everywhere: article captures, X posts, title cards, and end cards.
- For a newsy story, show several related X posts (about 3 to 6) so the viewer can see how widely it ran. Prefer official or high-engagement posts from accounts you confirmed.
- If a site blocks the capturer (a paywall or a bot wall), do not leave a blank frame. Build a custom dark headline card from the title.
- Cited YouTube clips stay muted. The music bed is the only soundtrack until Anthony adds his voice.
- The music is an original, quiet lofi bed at about -22 LUFS (safe range -24 to -20). The build also writes a separate music stem. The license is CC0 1.0. Do not use third-party samples.
- On-camera open and close are off by default. Turn them on only with `--on-camera-open-close` or `Camera: self` in the script.

## Credits

Credits are X-only. The build writes `post-attribution.md` next to the video. Paste that file into the post that ships the video.

Each credited account is a verified handle, written as `@handle (https://x.com/handle)`. Every X post that appears on screen also gets a direct link to that post. Do not list YouTube, news, or GitHub URLs in this file.

Never guess a handle. Confirm it with an X user lookup or a search, then store it in `handles.json`. If you cannot confirm a person or outlet, leave it out of the markdown. The build will record it under `unresolved` in `report.json`.

Known traps: Bloomberg's official handle is `@business`, not `@Bloomberg`. The AWS consumer handle is `@awscloud`. Jeff Geerling is `@geerlingguy`.

## How to make a video

Heavy work runs on the render host (iphedeiah), never on the box. The box only writes the script, looks up posts and handles, and copies files over SSH.

### 1. Write the script

Create `/workspace/edition-video/<EDITION>/script.md` from `reports/<EDITION>.md`. Aim for 700 to 1,100 narration words, or a little less for a short edition. One paragraph of narration per segment.

```
Edition: https://anthonyrussano.github.io/youtube-digest/reports/<EDITION>.html
## 01 Cold open
Style: montage
Narration: One paragraph that teases today's stories, in order.
Visuals:
- stat 61,764 | repositories scanned
- yt https://www.youtube.com/watch?v=ID @SECONDS | Lower-third label
- xpost https://x.com/handle/status/ID | @handle
- card A whole cloud, on a laptop.
- endcard Let's go.
## 02 First story
Narration: One paragraph that gets read aloud.
Visuals:
- page https://example.com/article | Site name | Fallback card title
- xpost https://x.com/handle/status/ID | @handle
- stat 14% | of hooks were wired to exit 2
## 06 Sign-off
Style: end
Narration: The playful goodbye.
Visuals:
- endcard Search your repos | Then make your hooks exit 2
- endcard See you tomorrow | anthonyrussano.github.io/youtube-digest
```

### 2. Shot types

- `yt`: a muted clip around the cited timestamp (`SECONDS-1` to `SECONDS+14`, at most 1080p, no cookies). A failed clip falls back to the thumbnail.
- `page`: a headless capture of an article, starting at the headline. Blocked pages become a title card. Light-only pages are inverted with photos kept, or placed on a dark framed card.
- `xpost`: a real screenshot of that post. The official dark embed (`https://platform.twitter.com/embed/Tweet.html?id=ID&theme=dark`) is tried first. If it does not render logged out, the build paints a dark card from X's public oEmbed. A `page` line that points at an x.com or twitter.com status URL is treated the same way.
- `card`: a dark headline card. Use this for a punchy line or a paywalled article.
- `stat`: a big number and a short label, on a dark card.
- `endcard`: a clean centered sign-off card. Use this in the outro, and for a short "Let's go" beat in the cold open.
- `edition`: the GitHub Pages edition page. Do not use this. It is off unless you pass `--include-edition`.

`Style: montage` (the default for a cold open) plays each visual once, in order, and does not cycle. `Style: end` (the default for a sign-off) holds on dark end cards.

### 3. Collect X posts and handles

Find 3 to 6 related posts per newsy story. Search with the `x` tools. Prefer official accounts and high-engagement posts from people you trust. Skip spam, replies, NSFW, and Grok or AI Overview posts.

Write the posts as `xpost` lines, or put them in `xposts.json` next to the script:

```
{
  "02": [
    {"url": "https://x.com/AikidoSecurity/status/123", "handle": "AikidoSecurity", "label": "Aikido Security"}
  ]
}
```

Confirm every handle you will credit, and write `handles.json`:

```
{
  "Aikido Security": "AikidoSecurity",
  "Lydia Hallie": "lydiahallie",
  "_entities": {
    "03": [
      {"entity": "Amazon Web Services", "handle": "awscloud"}
    ]
  }
}
```

`auto_xposts.py` can help. `auto_xposts.py queries script.md` prints a suggested search query per segment. `auto_xposts.py pick script.md results.json -o xposts.json` ranks a dumped search and picks about 3 to 6 posts per segment. Chosen URLs are also stored in `report.json` under `xposts`.

If you find no official post (this happened with the AWS Emulator launch), do not fill the gap with weak third-party posts. Use the article and title cards instead.

### 4. Render on the host

From the box:

```
tools/edition-video/remote.sh <EDITION>
```

That script copies the tools to `~/Projects/edition-video/bin/` on the host. It also copies the script and sidecars into `~/Projects/edition-video/<EDITION>/`, runs the build there, and copies the outputs back to `/workspace/edition-video/<EDITION>/`.

Useful flags (passed through to the build):

- `--segment 09`: render one segment, for a proof
- `--no-music`: skip the bed
- `--no-dark`: turn dark mode off (almost never what you want)
- `--on-camera-open-close`: leave the open and close out of the MP4 so Anthony can shoot them
- `--include-edition`: allow edition-page shots (do not use this)
- `--output name.mp4`: write a different filename in the work folder

To rebuild a cut without clobbering a delivered `final.mp4`, use a sibling work folder such as `/workspace/edition-video/<EDITION>-v2/`. Copy `script.md`, `handles.json`, and `xposts.json` into it. On the host, point `cache/yt` at the existing cache with a symlink. Copy the new file back as `final-v2.mp4`. Leave the delivered `final.mp4` untouched.

On the host directly: `~/Projects/edition-video/bin/build.sh <EDITION>`.

### SSH and ControlMaster rules

The host is `anthony@iphedeiah.lan`. Use the key at `~/.ssh/id_ed25519_iphedeiah`. Reuse the ControlMaster socket at `~/.ssh/cm-grokbot-%r@%h:%p`. Make at most two SSH attempts. Never probe the host with `nc` or `/dev/tcp`. A failed probe can get the box blocked for minutes.

Do not run yt-dlp, Chromium, ffmpeg, or `music.py` on the box. Those jobs belong on the host. YouTube also bot-blocks the box's IP.

### 5. What the capturer does

`capture.mjs` runs in headless Chromium on the host through Playwright.

Dark mode is on by default. The capturer sets `colorScheme: 'dark'` and Chromium force-dark. Cache keys include the theme and a page-crop version, so a logic change recaptures instead of reusing a stale PNG. Turn dark mode off with `EV_DARK=0` or `--no-dark`.

For an article, the capturer strips sticky and fixed chrome and finds the headline (`article h1`, `main h1`, `[itemprop=headline]`, or `h1`). It then starts the screenshot about 28 pixels above that headline. This keeps the title in frame. Older crops sometimes began at the byline and missed the `h1`.

If the capture is still light (this is common on CBS News), the build inverts the PNG. It pastes photos and color logos back so they do not look like negatives. Headless Chromium does not bake a CSS invert filter into screenshots, so the invert happens on the image, not in the page. If the result still looks wrong, the build places the readable article on a dark framed card with the headline above it.

For an X post, the capturer loads the official dark embed and crops the tweet card. If that embed does not render, `build.py` falls back to a dark oEmbed card.

### 6. Shot grammar

- Inside a segment, cuts are hard.
- Between segments, a short dip-to-black uses the 0.7 second breath at the end of the line. The first shot fades in. The last shot fades out a little longer.
- Stills and cards get a subtle Ken Burns push or pan. Cards move only 4 to 6 percent, so the type stays readable.
- Lower-thirds sit on a solid dark plate with a gold tick, not a see-through pill. If the lower-left corner of the frame is busy or bright, the label flips to the lower-right.
- A small chapter label fades on at the start of each story. It is skipped on `page` shots, because it collides with site navigation.
- The same shot type does not run more than twice in a row when another type is available.
- A consistent dark grade, a light vignette, and a little grain sit on every shot. Cards skip a second vignette, because they already have one painted in.

### 7. Music

`music.py` writes a procedural lofi-synth bed on the host. It is an original piece: a warm low-passed pad, electric-piano chords (Am9, Fmaj9, Cmaj7, Em7), soft bass, a swung drum loop at 80 BPM, and light crackle. There are no third-party samples. The license is CC0 1.0.

The loop is 16 bars (about 48 seconds) and joins cleanly, so a 5 to 8 minute video can repeat it. The file is faded in and out, then normalized in two ffmpeg `loudnorm` passes to about -22 LUFS.

Outputs: `music.wav` (24-bit, 48 kHz stereo) as the edit stem, `music.mp3` (192 kbps) for a chat-sized copy, and `music-license.txt`. Chat attachments must stay under 25 MB, so send the MP3, not the WAV, when you hand the stem off in chat.

Cited YouTube clips stay muted. Turn the bed off with `--no-music` or `EV_NO_MUSIC=1`.

## Outputs

After a successful build you should have these files in `/workspace/edition-video/<EDITION>/`:

- `final.mp4`: the silent (music-only) 1080p30 video
- `teleprompter.md`: narration with segment timecodes
- `post-attribution.md`: X credits to paste into the post
- `music.wav`: the full-quality stem
- `music.mp3`: the 192 kbps stem for chat
- `music-license.txt`: CC0 record
- `report.json`: sources, substitutions, failures, chosen posts, unresolved handles, music stats
- `timeline.json` and `attribution.json`: machine-readable companions
- stills you pull from the video for QA

Do not commit media, `data/`, `state/`, `subscriptions.csv`, secrets, cookies, or files marked "from transferred account". Commit only tool and doc changes. If a delivered `final.mp4` already exists, leave it in place and write a new cut as `final-v2.mp4`.

## Pacing and a recorded voiceover

Each segment lasts `words / 2.5 + 0.7` seconds. That is about 150 words a minute, plus a short breath. Teleprompter timecodes follow this clock and start at 00:00.0 with the cold open.

Anthony records to the teleprompter. A later pass can retime the picture to his real voice. To do that, transcribe the take, measure each segment's true duration, and scale or recut the shots so the picture follows his speech. The current build does not do this yet. Keep the teleprompter and the music stem so that pass has a clean starting point.

## QA checklist

Review stills from the final file before you hand it over. Pull one still from the cold open, one from each story, and one from the outro.

Check:

- No lower-third overlaps body text. The plate should be solid, and it should sit in the calmer lower corner.
- Article crops start at the headline, not at the byline or a tall header.
- No light pages in a dark video. If a site has no dark theme, you should see an inverted article with photos intact, or a dark framed card.
- No blocked or blank pages. A paywall (for example the Wall Street Journal) should be a title card, not a login wall.
- X posts are in dark mode, cropped to the post, and credited with a real handle.
- YouTube clips are on-topic at the cited time, and they are muted.
- The same shot type does not stack more than twice in a row when another type was available.
- Cards are sharp. Type does not collide with gold rules. Edges are not crushed by a double vignette.
- The music bed is quiet (about -22 LUFS) and fades in and out.
- `post-attribution.md` lists only confirmed handles and the posts that were shown. Nothing was guessed.
- The delivered `final.mp4` was not overwritten if you meant to ship a v2.

## Troubleshooting

- **ffmpeg n9 vignette modes.** ffmpeg 9 on the host accepts `mode=forward` or `mode=backward`, not `mode=auto`. The finish filter uses `vignette=angle=PI/5:mode=forward`. If a build still rejects the filter, the shot render retries without grain, then without the vignette.
- **Wall Street Journal is blocked.** The capturer hits a paywall or bot wall. Substitute a dark title card. Do not keep the blocked page on screen. Anthony preferred the card.
- **CBS News has no dark mode.** Force-dark leaves the page light. A CSS invert on the live page also fails, because headless screenshots drop a filter on `html`. The build then inverts the PNG and keeps photos. If that still looks bad, it frames the article on a dark card.
- **YouTube captions 429.** The digest pipeline can get rate-limited when it fetches captions. That is a fetch issue, not a video-render issue. The video tool does not need captions. It cuts from the cited timestamp in the edition script. Retry the caption fetch later, or use a cached transcript. Do not pass YouTube cookies unless Anthony already approved it.
- **Broken SSH pipe.** The ControlMaster socket went stale. Reconnect with the same options and the same socket path. Do not probe with `nc`.
- **Card edges look crushed.** An older finish applied a second vignette on top of the painted card vignette. Current builds use a lighter grade on cards and skip that second vignette.
- **A bare handle appears twice in credits.** If a post link for that handle is already listed, skip a bare handle line. Current `attribute.py` does this.

## Lessons and changelog

### First cut (2026-11-11-1710)

The first full video ran from the 1710 edition script. Anthony called it about 90 percent right. What worked: the voiceover-ready pacing, the muted cited clips, and the title cards for paywalled stories. What did not: shots of the edition page, too few X posts on a newsy story, and mixed light and dark captures. Credits were also easy to get wrong if a handle was guessed. On-camera open and close were tried, then dropped as the default. The delivered file stays at `/workspace/edition-video/2026-11-11-1710/final.mp4`. Do not overwrite it.

### v2 of 1710, and the 2235 edition

v2 added the montage cold open, dark end cards, and a CC0 music bed. It also tightened the cuts, added Ken Burns and lower-thirds, capped shot variety, and made dark mode the default. The 1710 v2 file is `/workspace/edition-video/2026-11-11-1710/final-v2.mp4` (5:19.5). The same tool then built the 2235 edition (Aikido stealer, Lydia Hallie's talk, AWS Emulator, Claude Code hooks) as `/workspace/edition-video/2026-11-11-2235/final.mp4` (4:04.2). Anthony liked both.

Lessons from those cuts:

- Never show the edition page.
- A cold open should tease each story once, in order, and then stop. Do not cycle the shots.
- Several official X posts beat a single screenshot. If no official post exists, do not scrape weak ones.
- Typography matters. Measure text with a real ink box so gold rules do not cover numbers.
- ffmpeg 9 is strict about vignette modes. Probe a short clip before a long render.
- Do not guess handles. Leave them unresolved.
- A transparent lower-third on a busy slide (a conference deck, or a dense blog) hides the words underneath. Use a solid plate, and pick the calmer corner.
- Start article crops at the `h1`. A crop that begins at the byline looks unfinished.
- Some sites will never go dark in the browser. Invert the image, or frame it. Do not ship a white article in a dark video.

A later pass of 2235 applies those last three fixes and writes `final-v2.mp4` next to the original.
