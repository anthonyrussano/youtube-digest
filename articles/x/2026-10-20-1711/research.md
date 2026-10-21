# Research: 2026-10-20-1711

## Lead candidates
| Story | Why lead | Coverage | Verdict |
|---|---|---|---|
| eMudhra intermediate CA key compromise | Actionable for every DevOps team today; affects servers, CI and containers | Headlines say "browsers patched, update your OS"; the per-layer trust store problem is under-explained | LEAD |
| SemiAnalysis: same B200, ~50% more output | Strong buyer lesson | Conference talk, little coverage | Also |
| Anthropic draft prospectus compute plan | Big number | Widely covered news | Also |
| Parcel Perform fine-tuning Nova | Practical, but podcast-only and long | Low | Also |
| AWS WAF cost dashboard | Practical how-to | Low | Also |

## Raw facts (lead)
- Cloudflare: learned Oct 19 ~17:00 UTC that private keys of eight eMudhra intermediate certificates were compromised; an attacker can forge a certificate for any domain. Patched WARP and cloudflared, mitigations across CDN/Developer/Zero Trust; no active exploitation found on Cloudflare services. Advice: "look beneath the SDK" (an API client may delegate verification to an HTTP library, runtime, OS or custom trust config); don't fix new cert errors by disabling verification; a passing browser test does not prove a background service is protected, nor does curl if the app uses a different verifier; rebuild images and reload/restart. https://blog.cloudflare.com/emudhra-certificate-compromise/
- Tracking site (Dennis Jackson): blocked in Firefox and Chrome since Oct 17, Apple since Oct 19, via OneCRL, CRLite and CRLSets; "many other clients do not consume revocation information and require software updates"; patched versions table (Ubuntu/Debian ca-certificates, Alpine 20261020-r0, Go 1.27.3/1.26.10, certifi 2026.10.19, pip 26.2.2, uv 0.13.4, rustls-webpki 0.103.16, Electron; Node.js, Bun, Fedora pending). https://emudhra.we-have-a-problem.com/
- Ubuntu: removed the two cross-signing roots (emSign Root TLS CA - G3, Comodo AAA Certificate Services); check with `dpkg -l 'ca-certificates' | grep ^ii`; fix `sudo apt install --only-upgrade ca-certificates`; unattended-upgrades applies within 24 h; browsers on Ubuntu Desktop are snaps and don't use the system store. https://ubuntu.com//blog/emudhra-ca-compromise-fixes-available
- Python (Seth Larson): upgrade certifi 2026.10.19, pip 26.2.2, uv 0.13.4, sigstore 4.5.1 in every venv and rebuild container images. https://discuss.python.org/t/information-for-python-users-regarding-emudhra-emsign-ca-certificate-security-incident/109576/1
- Private DevOps: every venv and container keeps the certifi it was built with; updating the host does nothing for running images; check a venv with grep -c "emSign ECC Root CA - G3" on certifi.where(), zero means removed. https://privatedevops.com/news/emudhra-ca-keys-leaked-updates
- Java: cacerts in $JAVA_HOME/lib/security; update JDK or remove emSign alias with keytool. https://lorbic.com/emudhra-ca-compromise-web-pki/

## What coverage misses
The fix is not one patch: a single host can hold four or five independent trust lists (OS bundle, each venv's certifi, the JVM cacerts, a Go binary built with an older toolchain, every container image frozen at build time). Browsers got protected silently, which makes it feel done.

## Angle
Your browser is already safe; your servers, CI runners and containers are not until you update each trust store separately and rebuild.

## Other items (facts from the website edition sources)
SemiAnalysis talk (3axY1wz2OvA t=230: 199 vs 298 tok/s per GPU, TensorRT-LLM no MTP vs SGLang + MTP on slide), Anthropic prospectus (AndrewCurran_), Parcel Perform (58ENTbfZD64 t=1953, 919), AWS WAF (BkzMdh_9EPY t=51, 229, 190 dashboard), Battle Drones (simonwillison.net), Laplace 3B (AWS ML blog), Vercel WebSockets GA.
