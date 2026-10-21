---
title: "Your browser already blocked the stolen eMudhra keys. Your containers didn't."
caption: "TLS tip: patching the host won't fix eMudhra. Every container image and Python venv keeps its own CA list, so rebuild..."
edition: "2026-10-20-1711"
lead_source: "https://blog.cloudflare.com/emudhra-certificate-compromise/"
---
The private keys of **eight eMudhra intermediate certificates** were [compromised](https://blog.cloudflare.com/emudhra-certificate-compromise/). With one of them, an attacker can create a certificate for any domain that your software will accept as real.

Your browser is probably fine already. Your servers, CI runners and containers probably are not.

## Why browsers were fast

Firefox and Chrome have [blocked these certificates since October 17, and Apple devices since the 19th](https://emudhra.we-have-a-problem.com/). Browsers can push revocation lists to every user in the background, so the fix was a switch someone flipped.

Most other software can't do that. It reads a fixed list of trusted authorities and **only changes when you update that list**.

## The part most coverage skips

There isn't one list. A single server can carry several, and each needs its own fix:

- **The OS bundle.** Ubuntu [removed the two roots that vouch for eMudhra](https://ubuntu.com//blog/emudhra-ca-compromise-fixes-available) from its ca-certificates package. Check with `dpkg -l 'ca-certificates' | grep ^ii`.
- **Every Python environment.** Requests and pip use certifi, their own copy of the list. Python's official advisory says [upgrade to certifi 2026.10.19, pip 26.2.2 and uv 0.13.4 in every virtual environment](https://discuss.python.org/t/information-for-python-users-regarding-emudhra-emsign-ca-certificate-security-incident/109576/1).
- **The JVM.** Java keeps its own `cacerts` file, so it needs a JDK update or [the emSign entry removed with keytool](https://lorbic.com/emudhra-ca-compromise-web-pki/).
- **Go and other runtimes.** The tracker lists [patched Go 1.27.3 and 1.26.10, rustls-webpki and Electron, with Node.js and Bun still pending](https://emudhra.we-have-a-problem.com/).
- **Every container image.** An image keeps the list it was built with. [Updating the host does nothing for the images running on it](https://privatedevops.com/news/emudhra-ca-keys-leaked-updates), so rebuild and redeploy.

## How to know you're done

Cloudflare's advice is to **"look beneath the SDK."** An API client may hand the certificate check to an HTTP library, the language runtime or the OS. [A passing browser test proves nothing about a background service](https://blog.cloudflare.com/emudhra-certificate-compromise/), and neither does curl if your app uses a different checker. Test through the app's own connection.

One more trap: after patching, some certificate errors may show up. **Don't fix them by turning verification off.** That removes the exact protection the update adds.

The takeaway: list every place your stack keeps trusted certificates, update each one, rebuild the images, restart, and test from inside the app.

## Also this cycle

- SemiAnalysis showed [the same B200 GPUs giving about 199 or 298 output tokens per second](https://www.youtube.com/watch?v=3axY1wz2OvA&t=230s) depending only on how the operator runs them.

[[IMG: /workspace/2026-10-20-1711-1-semianalysis.png | Slide from Oliver Kennon's SemiAnalysis talk on the AI Engineer channel, "Same GPU, 50% More Output": B200 output per GPU, 199 for TensorRT-LLM without MTP vs 298 for SGLang with MTP]]

- A WSJ report on [Anthropic's draft prospectus](https://x.com/AndrewCurran_/status/2112641878147649911) says it plans about three-quarters of a trillion dollars of compute over seven to ten years.
- Parcel Perform fine-tuned Amazon Nova and [the loss flattened after about 20% of its 10,000 samples](https://www.youtube.com/watch?v=58ENTbfZD64&t=1953s).
- AWS says one rate-based rule [cut a customer's WAF request volume 40%](https://www.youtube.com/watch?v=BkzMdh_9EPY&t=229s), and showed [a four-panel cost dashboard](https://www.youtube.com/watch?v=BkzMdh_9EPY&t=190s).

[[IMG: /workspace/2026-10-20-1711-2-waf.png | Four-panel AWS WAF cost dashboard from the Amazon Web Services video "AWS WAF cost budgeting & monitoring"]]

- Simon Willison's [Battle Drones RTS](https://simonwillison.net/2026/Oct/20/battledrones/) took 321 agent commits and became fun after one prompt: "Make it a LOT more fun."
- i14's [Laplace 3B keeps 29.5 MB of memory per conversation at any length](https://aws.amazon.com/blogs/machine-learning/beyond-the-kv-cache-training-and-serving-i14s-laplace-3b-linear-attention-model-on-aws-trainium2-with-native-pytorch/) on Trainium2.
- Vercel made [WebSockets in Functions generally available](https://vercel.com/changelog/websocket-support-is-now-generally-available), now at 15 million connections a day.

How many separate certificate lists did you find on one of your servers? Tell me which one surprised you.
