# Outline: 2026-10-23-1213 (roundup)

Title: Claude Code's sandbox stops the approval prompts. Its defaults still read your SSH keys.

1. Hook: everyone is sharing the one-flag sandbox trick. The docs' own defaults table is the part nobody screenshots.
2. What the trick does (OS-enforced, auto-allow, what still prompts).
3. What it doesn't cover by default: reads incl. ~/.ssh and ~/.aws; inherited env secrets; file tools / MCP / hooks outside; silent unsandboxed fallback; retry hatch.
4. Why the network half matters: Bloomberg DNS incident + frame; Claude Code's network design (no direct route out, can't even resolve a host without the proxy).
5. The five-line config: enabled, failIfUnavailable, allowUnsandboxedCommands false, credentials deny ~/.ssh ~/.aws/credentials + tokens; Read deny rules; update to 2.1.309; run the two probe commands. Frame 2 (three priorities).
6. Also this cycle: Vercel Agent plan scopes; Raw-RAG; Kimi K3.1 Pro; Dagger 1.0 beta; Nemotron 3.5 Bolt on Ollama; OpenAI Habitat.
7. Closing question.
