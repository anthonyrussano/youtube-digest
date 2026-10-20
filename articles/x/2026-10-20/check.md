# Check: edition 2026-10-20 (deep-dive), overnight prep

## Angle
- Real and overlooked: launch coverage on X (Oct 19-20) repeated "free scans, 77 critical / 803 high, curl fix". Almost none mentioned that Anthropic itself could only human-review about 6,000 of 29,000+ candidates, that the maintainer's lever is a written threat model with a severity rubric (and that OpenSSH, Valkey, Argo CD and Grafana already wrote theirs), or that curl moved LOW/MEDIUM reports into public issues the same week because of the report flood.
- Sourced: every claim links a primary source (Anthropic FAQ, launch post, enrollment repo, PM thread, curl advisory, Stenberg's posts, the projects' own threat_model.md files).
- Simple: PoC, model-rated and threat model are defined in plain words at first use.

## Rules
- Title names the lead idea (free AI bug finding vs. your threat model), not a list. No "$" + digit, no banned style name.
- Caption is tip-first ("Maintainer tip: ... write a threat_model.md ..."), ends in "...", no numbers as the hook, no "$" + digit.
- Lead length: about 680 words before "Also this cycle" (target 400-800). "Also this cycle": 5 linked one-liners.
- Ends with a takeaway and a reply-inviting question.
- No platform framing or engagement counts; the newsletter is not linked or named.

## Fact checks made (changes to article.md)
- "flood of AI-found reports" softened to "a flood of vulnerability reports, many of them found by AI" (Stenberg blames the report avalanche, and separately notes many are AI-found).
- "write a fix" changed to "propose a patch" (FAQ wording).
- "Nearly 5,000 more" changed to "Nearly 5,000" (the 5,000 sent unverified is not stated to be on top of the 6,000 reviewed).
- "no real app would use" changed to "unlikely to ever be used in the real world" (Stenberg's wording).
- OpenSSH line: dropped "Only" (the file says a controlled overflow that may lead to RCE should be critical; it doesn't say only that).
- Coinbase one-liner reworded to match the transcript (goal of 25,000 by year end; by year end one every 17 seconds, t=202-208).

## Images (every number and label checked)
1. `/workspace/2026-10-20-1-oss-scanner-flow.png` (pele flow diagram, dark). Steps checked against https://red.anthropic.com/oss-scanner and https://github.com/anthropics/oss-scanner README: PR adding projects/NAME/project.yaml; human review of maintainer and security contact ("Every sign-up request is reviewed by a human"); Dockerfile build in an isolated VM with network on; scan with no Internet access; threat_model.md read before the scan (template comment "the scanner reads it before it starts"); agents double-check bugs, root cause, PoC and patch (FAQ, launch post); encrypted email (PM thread: "Now, all reports arrive encrypted"); model-rated, no human review, no 90-day clock (FAQ "public disclosure policy"). No numbers in the image.
2. `/workspace/2026-10-20-2-found-vs-reviewed.png` (chart-generator column chart, dark). Data file values: Found by models 29000, Reviewed by humans 6000, Sent unreviewed on request 5000. Source: https://www.anthropic.com/research/launching-opt-in-vuln-finding-service-for-open-source ("over 29,000 candidate vulnerabilities", "approximately 6,000", "nearly 5,000 reports" sent unverified at maintainers' request, "to date"). The subtitle states the approximations ("over", "about", "Nearly") and the time frames (six months; to date). chart-generator blind-spots report: no errors, missing or unparsed values.
3. `/workspace/2026-10-20-3-threat-model.png` (screenshot, box browser, cropped): https://github.com/anthropics/oss-scanner/blob/main/templates/threat_model.md in Preview mode. Text matches the raw template file. No numbers.

## Tool check
- `./run.sh x-article 2026-10-20 --dry-run`: FORMAT deep-dive, SOURCE articles/x/2026-10-20/article.md, title and caption guards pass.

## Draft website edition (draft-report.md)
- STYLE checklist run: front matter title/dek quoted; cold open of two linked hits, one-line intro, 17 items, sign-off; no headers, bullets or tables; the platform-word grep prints nothing; the one transcribed video is cited with timestamped links; X items come from the selected posts; AINews stories link original sources only.
- A trial render (copied to articles/, rendered, then both files deleted, nothing committed) passed: 1 video cited, 0 on the radar.
