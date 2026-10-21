# Outline: 2026-10-20-1711 (roundup)
1. Hook: browsers blocked the stolen eMudhra keys days ago; your servers probably still trust them.
2. What happened, plainly: eight intermediate CA private keys leaked; anyone with them can mint a valid-looking cert for any site.
3. Why browsers were quick: they push revocation lists (CRLSets, OneCRL, CRLite). Most other software just reads a static list and needs an update.
4. The missed part: there is not one list. OS bundle, each Python venv's certifi, JVM cacerts, Go toolchain, every container image frozen at build time.
5. Checklist: apt/apk ca-certificates; certifi/pip/uv in every venv; JDK; Go rebuild; rebuild and redeploy images; test through the app's real TLS path; never disable verification.
6. Also this cycle (bullets): SemiAnalysis operator (with frame), Anthropic prospectus, Parcel Perform fine-tuning, AWS WAF costs (with frame), Battle Drones, Laplace 3B, Vercel WebSockets.
7. Closing question: how many separate trust stores did you find on one box?
