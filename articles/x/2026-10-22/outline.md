# Outline (roundup, in-depth lead + short "Also this cycle")

## Lead: you may already own most of an "AI SRE"
1. Hook: same agent (Claude Code), same model, same 50 broken Kubernetes clusters. Only change: what it can read.
   With read-only "what is failing / what changed" context it was right inside two minutes on 86% of faults vs 60%
   with a shell.
2. Plain-language "context": four things (current failures, change timeline that outlives 1-hour events, linked
   resources, error-only logs). The agent asked for "what's failing" first on all 50, "what changed" second on 35.
3. The example: missing CART_ADDR env var. Shell: 58 calls, ~12 minutes, ended decoding Helm's release Secret.
   Context: 7 calls, 35 seconds.
4. What most coverage skipped: what the shell agent did while "just investigating". Own pods on 13 faults; exec/cp/
   port-forward/debug on 21; pulled Secrets into context on 4; dropped two MongoDB collections to test a theory,
   then got the diagnosis wrong. An agent told to fix things uses write access while still guessing.
5. Takeaway / how-to: give the agent a view-only identity (built-in `view` role: no Secrets, no exec), short-lived
   token, kubeconfig without your admin user; check `kubectl auth can-i get secrets` says no. Then measure at a fixed
   time limit before buying anything.
6. Honest caveats in one line: vendor-run (Radar), one run per fault, the arms also differed in write access.
Images: chart (2-min / 5-min shares) after point 1.

## Also this cycle (bulleted one-liners)
- php2shell: patch the PHP runtime, not just plugins (OpenAI/Calif/Wiz finding; Cloudflare WAF rules 9 h early).
- MCP supply chain: the Postmark MCP one-line BCC (video frame).
- Anthropic API version 2026-10-21 drops temperature/top_p/top_k; new SDKs default to it.
- Claude Duet research preview.
- GitHub per-reference write quorum, 3-4x throughput.
- OTel Collector recipe to trim Claude Code telemetry (181 records / 289 KB for one small task).
- Air Canada: write the answer first; 275 generated tests.

## Close
Question: Would you let an agent near prod with your kubeconfig, or does it get its own view-only identity? What does
yours run as?
