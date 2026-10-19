---
title: "Your agent's tool list can cost 54,500 tokens before it starts. Grafana cut it to 504."
caption: "Agent tip: load tool manuals on demand, not upfront. Grafana cut its agent's tool definitions from 54,500 tokens to 504..."
edition: "2026-10-19-1211"
lead_source: "https://grafana.com/blog/six-improvements-that-make-grafana-assistant-better-at-helping-your-workflows/"
---
Grafana's AI agent used to spend about **54,500 tokens** just describing its tools before it read a single question.

Now it spends **504**.

That number sits halfway down [a Grafana Labs post](https://grafana.com/blog/six-improvements-that-make-grafana-assistant-better-at-helping-your-workflows/) about six months of fixing Grafana Assistant. The bigger lesson is in the pattern behind it: most of their wins came from fixing the interface around the model, not the model itself.

## The results first

Dashboard building is about 27% of Assistant conversations. Over roughly 10 weeks, Grafana says the reported error rate there fell from **2.47% to 0.65%**.

The slowest 5% of operations went from 63 seconds to **28.8 seconds**. Cost per request fell **18%**.

Here is how they got there.

## 1. Don't load every manual upfront

An agent learns what its tools do from **tool definitions**: a name, a description and the inputs each tool takes. Most setups paste all of them into the prompt at the start of every chat.

Grafana flipped that. The agent starts with a few **compact entry points** and pulls the detailed instructions for a tool only when it needs that tool.

That is how the starting overhead went from about 54,500 tokens to 504, a 99.1% cut. Grafana is careful here: real savings depend on which tools a chat uses, and they still measure the whole task, because looking things up can add steps.

## 2. Make the CLI talk back

Grafana watched agents use its command-line tool and saw the same mistakes again and again. They **guessed flags**, **retried failed commands** and **asked for far more output** than they needed.

So they built **gcx**, a CLI designed for agents. Commands describe what they can do. **Errors explain how to recover.** Agents can see the available fields and filter results before anything lands in their context.

Their design question is worth stealing: **what should the interface tell the agent so it can take the next step correctly?**

## 3. Grade the work, not the answer

An agent can give a convincing answer while the work underneath is wrong. A dashboard panel can render fine and still show the wrong math.

So Grafana's graders check the **queries, tool calls and saved state**, not just the final reply. Every failure found in production becomes a repeatable test. The dashboard test set grew from **78 scenarios to nearly 200**.

They also tried a cheaper, faster judge model. It agreed with their best reviewer much less often, so they kept the stronger judge for the main score.

## 4. Small context fixes beat clever prompts

On real past incidents, one agent **guessed too much from an alert's name**. Fetching the actual alert definition fixed it. Another agent skipped a useful tool because its instructions described **the wrong query language**.

Fixes like these moved their hard-incident test score from **52% to 69%** in a week.

## The takeaway

If you build an MCP server, a CLI or any tool an agent calls, check two things today. How many tokens do your tool definitions cost before the first question? And when a command fails, does the error tell the agent what to do next?

What does your agent waste the most tokens on before it gets to work?

## Also this cycle

- Jediah Katz, who built Cursor's agent harness and is now at SpaceXAI, says his team logs every guardrail "shim" and [a bot opens a PR to delete any that stops firing](https://www.youtube.com/watch?v=7Y4sbZgBdnc&t=1002s).
- Cua's [Spaces SDK](https://x.com/trycua/status/2112228154651881479) puts Claude Code, Codex or any agent on a desktop you choose, from your laptop to [your own AWS, Google Cloud or Azure account](https://x.com/trycua/status/2112228156958822650).
- Cloudflare previewed [Clairic](https://blog.cloudflare.com/clairic-extraction-model/), an extraction model that returns typed values in one pass and bills only input tokens.
- AWS showed [bi-directional KV cache transfer in vLLM](https://aws.amazon.com/blogs/machine-learning/improve-ttft-for-multi-turn-agentic-workloads-with-bi-directional-kv-transfer-in-vllm/), cutting time to first token up to 3.3x for multi-turn agent chats.
- Unsloth shrank [DeepSeek V4.1 Flash](https://x.com/UnslothAI/status/2112212605930778830) from 508 GB to 250 GB so it runs on a 128 GB RAM machine.
- [CERN and Mistral](https://home.cern/cern-and-mistral-join-forces-to-accelerate-ai-for-science/) plan a Large Physics Model trained on billions of simulated LHC collisions.
