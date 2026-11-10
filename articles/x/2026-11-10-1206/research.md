# Research: 2026-11-10-1206 (classic roundup)

Sources: the edition's cited links only (Railway incident report, DeepMind Gemini 4 Carbon post, GitHub Git security post, CNCF posts on OpenShell, Jaeger and CloudNativePG, LangChain Deep Agents post, OpenAI Businesses in ChatGPT, and the X posts cited in reports/2026-11-10-1206.md).

| Candidate | Why lead | Coverage | Verdict |
|---|---|---|---|
| Railway Oct 21 attack report | Full chain from build escape to decrypted AI keys; concrete fixes any platform team can copy | New today; most reactions quote the headline, few walk the credential hops | Lead |
| Gemini 4 Carbon GA | Biggest brand, benchmark and price facts | Widely covered | Second |
| Git 2.56.1, six CVEs | Actionable: update Git and bundled copies | Advisory-level coverage | Third |

Lead facts (Railway report): partial isolation escape on a shared build VM at 07:28 UTC Oct 20; build credential accepted by internal Temporal as a trusted client; 353 build histories read and a monorepo copy fetched; a wrong OIDC binding in CI gave short-lived cloud credentials at 03:26 UTC Oct 21; SSH to an orchestration machine with a long-lived decryption credential on disk; queries matched variable names against regexes for AI provider keys; at most 1.85% (~100,000) workspaces; 1,852 users' linked-account tokens reset; ~740,000 dollars estimated unauthorized spend; each build now gets its own ephemeral VM with a push-one-image credential.

Angle: every hop was an over-trusted credential, and attacker agents made the hops fast.
