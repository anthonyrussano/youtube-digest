# Research: 2026-10-23-1213

## Candidates

| Story | Big-name tool | Coverage today | Overlooked angle | Verdict |
| --- | --- | --- | --- | --- |
| Claude Code sandbox "stop approving every command" trick (viral thread) | Claude Code | Viral "save it" thread; several changelog recaps of v2.1.309 | Defaults still let sandboxed commands read ~/.ssh and ~/.aws and inherit env secrets; it silently runs unsandboxed if a dependency is missing; file tools, MCP servers and hooks run outside it; 2.1.309 just fixed shell startup files running outside the sandbox. Bloomberg's DNS-exfiltration incident shows why the network half matters | LEAD |
| Vercel Agent plan-scoped production access | Vercel | Vercel blog only | Approval fatigue fix: one plan approval grants scopes, short-lived tokens | Also-this-cycle (pairs with lead theme) |
| Raw-RAG beats agentic memory | (research) | omarsar0 thread | Run the baseline first; 0.3 h vs 3.2-27 h ingest | Also |
| Kimi K3.1 Pro | Kimi | HN | Open weights by Nov 4, Terminal-Bench 65.7% vs Opus 5.5 66.4% | Also |
| Dagger 1.0 beta | Dagger | Launch post | CI for agent-speed | Also |
| NVIDIA Nemotron 3.5 Bolt E4B on Ollama | NVIDIA/Ollama | Launch posts | 4GB local model | Also |
| OpenAI Habitat storage Part II | OpenAI | Eng blog | 10K RU/s partition limit | Also |

## Sources checked (lead)

- Claude Code docs, "Configure the sandboxed Bash tool": https://code.claude.com/docs/en/sandboxing
  - Off by default; /sandbox or sandbox.enabled true. OS enforces limits while command runs, so sandboxed commands can run without approval (auto-allow mode).
  - Defaults table: writes = working dir, per-user temp dir, added dirs; reads = "Most of the machine, including credential files such as ~/.ssh and ~/.aws/credentials"; network = no direct route out, proxy, allowed domains start empty; env vars inherited "including any secrets in its environment".
  - Outside the sandbox: Read/Edit/Write/WebFetch/WebSearch, hooks, local MCP servers, status line, apiKeyHelper ("run with your full access"); `!` commands you type; excludedCommands; unsandboxed retries (dangerouslyDisableSandbox).
  - Warning: by default if sandbox can't start (missing dependency / unsupported platform) Claude Code runs commands without sandboxing; failIfUnavailable true makes it exit instead.
  - allowUnsandboxedCommands false disables the retry escape hatch ("Strict sandbox mode").
  - Auto-allow still prompts: Bash deny rules, rm/rmdir on critical paths, content-scoped ask rules like Bash(git push *).
  - Linux/WSL2 needs bubblewrap and socat. Native Windows runs unsandboxed.
  - Network: Linux separate network namespace; UDP/QUIC/ICMP can't leave; `curl --noproxy '*' https://example.com` fails with "Could not resolve host".
  - sandbox.credentials deny entries: block file reads and unset env vars for sandboxed commands; "There is no built-in credential deny list".
  - Sandbox doesn't cover the Read tool: use Read deny rules (permissions page; also confirmed via search result).
  - Test: ask Claude to run `touch ~/sandbox-probe` (should fail) and `curl --noproxy '*' https://example.com` (should fail).
- Claude Code CHANGELOG 2.1.309: "Fixed sandboxed Bash commands on macOS and Linux running the shell's startup files outside the sandbox before each command"; "Fixed sandboxed commands and auto-accepted edits being able to modify the MCP config file passed with --mcp-config"; "Linux: Fixed sandbox write denies lifting when a background command outlived the session". https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md
- Viral thread (inspiration, not cited as fact; includes a promo for an unrelated product, omitted): https://x.com/thedelost/status/2113664890955084221
- Bloomberg talk (AI Engineer, Andrey Rybka, "Real AI Agent Attacks and What Would Have Stopped Them"): https://www.youtube.com/watch?v=5O6jLtoeKrg
  - t=83 agents took 17,600 actions in four and a half days (sandbox escape via package-proxy zero-day, lab unnamed).
  - t=524-551 sandbox with no web access, "we forgot about DNS"; data smuggled out via DNS lookups; fix: default deny for all outbound traffic including DNS. Slide: "They blocked the web, but not DNS ... Fixed Feb 2026", homework "Can your agent sandbox do DNS lookups?"
  - t=861-896 three priorities slide: lock down agent actions; one agent one identity; box the runtime (sandbox, default-deny egress DNS and metadata included, budgets that halt).

## Coverage check

- Web search for the sandbox defaults found the docs and a GitHub docs issue; X search (since 2026-10-21) shows the viral "save it" thread plus short v2.1.309 changelog recaps. None of them pair the tip with the default read access to ~/.ssh/~/.aws, the silent unsandboxed fallback, or the DNS lesson. That is the angle.
