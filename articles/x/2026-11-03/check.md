# Check: 2026-11-03 (classic full roundup, overnight prep)

## Winning-formula rules
- [x] Body = the full edition: same 17 stories as draft-report.md, cold open with hard numbers (petabyte a day, 100,000 lines of C), the fixed intro line, 18 story paragraphs plus "A few quick ones.", no `##` sections, no bullets. `x-article --dry-run`: 25 paragraphs, ~1,790 words.
- [x] Title: three named items with numbers and verbs, Oxford comma, 97 characters: "OpenAI cuts Git push latency 80%, Mixedbread lifts an agent to 98%, and GhostAction hits 30K repos". 80% = OpenAI's "nearly 80%" median push latency cut; 98% = Mixedbread's claimed answer accuracy; 30K = "over 30,000 repositories" (video, 0-7 s).
- [x] Caption: "Codex tip: ..." tip-first, then "Meanwhile" + surprise, 229 characters, ends in "...", no `$<digit>`, no banned style name. The tip comes from OpenAI's Pando post (built with Codex, conformance suite + deterministic simulation, 10 weeks).
- [x] Images: 3 inline markers, each on its own line right after the paragraph citing its source; 2 cited-video frames (slides, not talking heads) + 1 diagram. NASA Earth header prepared.
- [x] Close: reply question with three choices, then sign-off.
- [x] `./run.sh x-article 2026-11-03 --dry-run` prints FORMAT roundup and SOURCE: articles/x/2026-11-03/article.md.

## STYLE.md checklist (draft-report.md)
1. [x] Quoted title (teases Pando, Battlefield 1942, GhostAction) and quoted dek (contrast: petabyte a day vs one YAML file).
2. [x] Cold open of two linked hits, intro line, items, sign-off.
3. [x] `grep -nE '^(#|[-*] |\|)'` prints nothing.
4. [x] 17 items (13 full paragraphs + 4 quick ones), each with who, what, a number, why it matters.
5. [x] No repeats: checked against reports 2026-11-01*, 2026-11-02 and 2026-11-02-1213 (weight-space programming and Anthropic Q3 dropped as already covered). All 8 transcribed videos are linked with `&t=` links.
6. [x] X items only from data/x_selected.json, written like video items; platform grep prints nothing.
7. [x] Vendor numbers attributed (Mixedbread "claims", Gartner analysts, OpenAI "says", LangChain "says"); extrapolations flagged (Q Labs); no crypto/spam.
8. [x] Craft: ban-list grep clean; contrasts: big/small (petabyte a day vs one YAML file), claim/reality (Gartner 20x vs 5-6x real; open-model savings vs H200 that cannot pay its rent), before/after (36% -> 98%, 1,227 MB -> 66 MB), X-but-Y (Lacey builds MCP, his agents skip it).

## Fixes made during check
- Wrong attribution caught and fixed: the first draft put a wrong name on the poteto post; it now says Lauren (the account's display name), who mentions updating pstack in the post.
- "T5-family decoders" -> "UMT5's decoder" (the blog names UMT5).
- GitHub blocking timestamp moved to 127 s (where "october 9th" is said); cache-point timestamp to 449 s.
- Gartner "harnesses" line reworded to match the reporting ("the analysis casts harnesses ... as the valuable part").
- "This week" -> "Now" for the Battlefield port (post dated Nov 2).
- "looks like" -> "points to" (clean platform grep).

## Images: every number, label and name checked
1. `/workspace/2026-11-03-1-pando-flow.png` (diagram, pele, dark): labels from https://openai.com/index/scaling-git-at-openai/ : pack validated in a single pass without unpacking (push section); pack stored as immutable blob in blob store (causal consistency section); metadata store records a ref version (push section); fetch selects stored packs covering what the client needs (fetch section); packfile URIs instead of a fresh pack (empty inline pack, packfile-uri); Express regional cache, "cache hit rates of over 99%". Only number: 99%. OK.
2. `/workspace/2026-11-03-2-mixedbread-accuracy.png` (video-frame): https://www.youtube.com/watch?v=3Ad73Onx3Aw&t=904s, AI Engineer channel. Slide reads "Production customer: 36% -> 98%", "A hedge fund's agent benchmark, 55 questions on their own documents. They only swapped the search backend.", Before 36%, With Mixedbread 98%. Matches transcript 904-912 s. Speaker is in a corner inset; the slide is the subject.
3. `/workspace/2026-11-03-3-aws-failures.png` (video-frame): https://www.youtube.com/watch?v=WD0caEH76og&t=185s, Amazon Web Services channel. Slide "Where critical failures originate", first six months 2026: service configuration 30%, performance and timeouts 21%, service limits and quotas 13% (alt text uses only these three), marked "Approximate figures, rounded". Transcript 185-190 s says "about a third". OK.
- Dropped: a GhostAction frame at 142 s (chapter title card, no useful content).

## Header
- iss071e439624, "An orbital sunrise colorfully illuminates the Earth's atmosphere" (ISS, Aug 6, 2024, above the Pacific north of Auckland), NASA public domain, orig JPEG 4928x2768, 637 KB, viewed. The private post log was not available on this box this run, so the id was checked against every header id in committed overnight.json files and the git history (no match); the 10:37 poster should re-check against state/x_posts.json if it exists by then.
