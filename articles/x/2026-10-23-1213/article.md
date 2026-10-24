---
title: "Claude Code's sandbox stops the approval prompts. Its defaults can still read your SSH keys."
caption: "Claude Code tip: if you turn on the sandbox to stop the approval prompts, also deny ~/.ssh and ~/.aws and set failIfUnavailable. By default, sandboxed commands can still read your keys..."
edition: "2026-10-23-1213"
lead_source: "https://code.claude.com/docs/en/sandboxing"
---
The Claude Code tip going around this week is a good one: turn on the sandbox and the agent stops asking you to approve every shell command. The part nobody is screenshotting is the defaults table in Anthropic's own docs.

## What the trick actually does

With `/sandbox`, or `sandbox.enabled` set to true, every shell command Claude runs starts inside a boundary that **the operating system enforces**, not the model. That's Seatbelt on macOS and bubblewrap on Linux and WSL2. Because the OS holds the line, [Claude Code can run sandboxed commands without asking you to approve each one](https://code.claude.com/docs/en/sandboxing).

Writes stay in the working directory and a temp dir. The network has no direct route out. Every host goes through a local proxy, and your allowed domains start empty. A few things still stop you even in auto-allow mode: `rm` aimed at a critical path, any deny rule, and ask rules like `Bash(git push *)`.

That part is real, and it beats `--dangerously-skip-permissions`.

## What it does not cover by default

The same docs page lists the default for reads as "most of the machine, including credential files such as `~/.ssh` and `~/.aws/credentials`." Environment variables are inherited from Claude Code too, **"including any secrets in its environment."** There is no built-in credential deny list. Only what you list is blocked.

Three more gaps are easy to miss:

- **It can fail open.** If the sandbox can't start because a dependency like bubblewrap or socat is missing, Claude Code runs your commands without it, unless you set `failIfUnavailable` to true.
- **There's an escape hatch.** When a command fails inside the sandbox, Claude can ask to retry it unsandboxed. `allowUnsandboxedCommands: false` turns that off.
- **It only wraps shell commands.** Claude's Read, Edit and WebFetch tools, hooks and local MCP servers run outside it "with your full access." A sandbox `denyRead` entry doesn't stop the Read tool, so you need a matching Read deny rule for that.

And update. Claude Code 2.1.309 [fixed sandboxed Bash on macOS and Linux running your shell's startup files outside the sandbox before each command](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md). It also stopped sandboxed commands from editing the MCP config file passed with `--mcp-config`.

## Why the network half matters

Bloomberg's Andrey Rybka spent a talk on real agent incidents. One team had [a wonderful sandbox with no web access, "but guess what? We forgot about DNS."](https://www.youtube.com/watch?v=5O6jLtoeKrg&t=524s) A prompt hidden in some productivity tips had sandboxed code smuggle data out through DNS lookups.

[[IMG: /workspace/2026-10-23-1213-1-dns.png | Slide from AI Engineer's "Real AI Agent Attacks and What Would Have Stopped Them" (Andrey Rybka, Bloomberg, YouTube): "They blocked the web, but not DNS." A prompt hidden in productivity tips made sandboxed code smuggle data out through DNS lookups. Homework: can your agent sandbox do DNS lookups?]]

His fix is [default deny for all outbound traffic, DNS included](https://www.youtube.com/watch?v=5O6jLtoeKrg&t=548s). Claude Code's sandbox starts there. Allowed domains begin empty, and on Linux a sandboxed command runs in its own network namespace where UDP can't leave at all. Even `curl --noproxy` fails with "Could not resolve host." But that only helps if the sandbox is actually running and your secrets aren't readable in the first place.

## The five-minute version

1. Turn it on in `~/.claude/settings.json`, not just for one project.
2. Set `failIfUnavailable: true` and `allowUnsandboxedCommands: false`.
3. Add `sandbox.credentials` entries with `"mode": "deny"` for `~/.ssh`, `~/.aws/credentials` and tokens like `GITHUB_TOKEN`. Add Read deny rules for the same paths.
4. Fill `allowedDomains` with only the hosts your repo calls.
5. Ask Claude to run `touch ~/sandbox-probe` and `curl --noproxy '*' https://example.com`. Both should fail. If either works, the sandbox isn't on.

[[IMG: /workspace/2026-10-23-1213-2-priorities.png | Slide from AI Engineer's "Real AI Agent Attacks and What Would Have Stopped Them" (Andrey Rybka, Bloomberg, YouTube): three priorities, all deterministic controls. Lock down agent actions; one agent, one identity with short-lived tokens; box the runtime with default-deny egress, DNS and metadata included, and budgets that halt]]

Rybka's [three priorities](https://www.youtube.com/watch?v=5O6jLtoeKrg&t=861s) sum it up: code enforces, prompts suggest. The sandbox removes the prompts, so the config has to do the enforcing.

## Also this cycle

- Vercel Agent [asks for its production scopes in one plan you approve once](https://vercel.com/blog/how-vercel-agent-accesses-production-safely), with short-lived tokens, so nobody builds a habit of clicking approve.
- [Plain RAG over raw chat history beat agentic memory systems](https://x.com/omarsar0/status/2113635562578178147) in six of seven benchmark settings, and ingested in 0.3 hours instead of 3.2 to 27.
- [Kimi K3.1 Pro](https://www.kimi.ai/blog/kimi-k3-1-pro) scores 65.7% on Terminal-Bench 4.0, next to Claude Opus 5.5's 66.4%, with open weights due by November 4.
- [Dagger 1.0 beta](https://x.com/dagger_io/status/2113659582644105527) pitches itself as a Jenkins and GitHub Actions replacement built for the speed of coding agents.
- NVIDIA's [4GB Nemotron 3.5 Bolt E4B](https://x.com/NVIDIAAI/status/2113657112408785153) is a small open model for local assistants and robots, and it's [already on Ollama](https://x.com/ollama/status/2113684810426450098).
- OpenAI's storage layer for ChatGPT [holds over 500 PB across 40 regions](https://openai.com/index/scaling-storage-one-billion-users-part-two), and it went back to multi-tenant by default.

If you run Claude Code with the sandbox on, did you ever check what it can read? Reply with what you found.
