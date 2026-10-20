# Outline: deep-dive, edition 2026-10-20

Core idea: AI can now find serious bugs for free; the scarce resource is human triage, and the lever a maintainer (or any team) controls is a written threat model with a severity rubric.

1. Hook: curl's worst bug in years (CVE-2026-92392, an HTTP/2 upload use-after-free) came from an AI scanner. The same week, curl said the AI report flood is drowning it. Both are true, and that is the story.
2. What launched: Anthropic's OSS Scanner, free periodic scans of critical open source, PoC + patch per finding. First numbers (114 of ~650 accepted, 77 critical + 803 high model-rated findings). Plain-language: "model-rated" means the model picked the severity, no human checked it.
3. How it works (diagram): PR with project.yaml, human checks the maintainer, your Dockerfile builds online, Internet cut, agents audit, double-check, write PoC + patch, encrypted email. No 90-day clock on these unreviewed reports. Define PoC = a small program that proves the bug.
4. The overlooked part, the bottleneck (chart): Anthropic found 29,000+ candidates in six months but humans reviewed about 6,000. That gap is why this lane skips review. Quality is high (85 of 97 audited met the bar; 1 false positive), but maintainers said severity is sometimes inflated or the threat model misunderstood.
5. curl's answer: from Oct 26, LOW and MEDIUM reports go to public GitHub issues; over 90% of submissions are below HIGH. AI tries "crazy combos" nobody uses.
6. The lever: threat_model.md. What goes in it (untrusted input, what matters, how to run it, severity rubric, what to skip). Real examples: OpenSSH (any UAF is high+, controlled overflow to RCE is critical), Valkey (CVSS vector required; Medium/Low fixed publicly), Argo CD (attackers to consider and who is trusted). Screenshot of a real one.
7. Takeaway: write the file even if you never enroll; it works for any agent doing a security review. Also: make your project build offline in one Dockerfile.
8. Question: would you hand a model your severity rubric, or keep triage human?
9. Also this cycle (5): ECDSA seeds; Terminal Bench 4 audit; Coinbase x402; Muse Glimmer; vLLM v0.32.0.
