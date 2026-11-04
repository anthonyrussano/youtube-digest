# Outline: 2026-11-04 (classic full roundup)

Cold open: NatWest's LLM judge looked fine on average error (0.2) but correlated 0.04 with humans. Meanwhile Devin ran nine cloud Macs at once. Then the fixed intro line.

Lead (NatWest), one idea per paragraph:
1. Who and stakes: 19 million customers, 100,000 conversations a day, a third of journeys moving to AI. The risk is blast radius, not the model.
2. Shrink first: the routing funnel. Rules bracket the model; fewer than half of turns reach it; the classifier is an MLP. [frame t=300]
3. The overlooked part: measuring. One 83% pass rate hid 97% vs 43%; humans agree only 64% on intent; the judge's 0.04 correlation; swapping only the judge model moved headroom from 0.08 to 0.02. Fix: judge from another model family, check correlation and spread. [frame t=600]
4. Shipping: sample 5% plus every handoff/failure, score every 4 hours, regression gate on every merge, shadow first, brand by brand, roll back in seconds. Takeaway line. [diagram: safety spine]

Other items, one paragraph each (neighbors differ):
- Red Hat / OpenShell: trusted gateway vs untrusted sandbox; deny by default, approve at runtime. [diagram: trust zones]
- AMD vs Intel: 13.4 bn, data center +97%, about 17 bn vs 15-16 bn. [chart]
- Devin nine Macs (promotional, Cognition employee).
- Claude Code 2.1.317 game rule fix.
- vercel doctor (ship doctor subcommands).
- Alloy 1k robots playbook (vendor claims).
- agent-desktop accessibility tree.
- "A few quick ones." Screenplay; Latent Sparse Attention (relayed, primary page).

Close: reply question with three choices (judge correlation check, OpenShell-style sandbox, a doctor command), then sign-off.
