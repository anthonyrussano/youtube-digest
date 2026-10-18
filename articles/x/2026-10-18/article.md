---
title: "DeepSeek bills agent web search per call, not per result. Search wide once."
caption: "Agent tip: on DeepSeek's new Search API, ask for 50 results with need_content on and drop anything under rerank_score 1.5 before fetching. You pay per call, not per result, and Claude Code and Codex search calls start billing Nov 1..."
edition: "2026-10-18"
lead_source: "https://api-docs.deepseek.com/guides/search/"
---
DeepSeek just put a price on web search for AI agents: **0.75 dollars per 1,000 calls**.

That number is what everyone shared.

The more useful part is the unit. You pay **per successful call**, not per result. And that changes how an agent should search.

## What shipped

DeepSeek opened two APIs, [Search and Fetch](https://api-docs.deepseek.com/guides/search/).

**Search** takes a question and returns a list of web pages, from DeepSeek's own search engine.

**Fetch** takes one URL and returns that page as clean Markdown text.

Both use the same API key as DeepSeek's models. They are built for agents and RAG apps, meaning apps that look things up before they answer.

## The unit is the story

A search call can return anywhere from 1 to 50 results. **The price is the same either way.**

You are only billed when the call works and finds something. Empty results, errors and timeouts cost nothing.

So the cheap pattern is not "search narrow, then search again." It is **one wide search** that asks for 50 results.

## Skip the second call

Most agents search, then fetch each page they like. That is one call per page.

DeepSeek's search has a flag, **need_content**. Turn it on and the page content comes back inside the search results.

Each result also carries a **summary** of 600 to 800 characters that the docs say is meant to be read by a model.

For many questions, that is enough. No fetch needed.

## Filter before you read

Every result has two scores.

**rerank_score** runs from 0 to 3. DeepSeek counts 1.5 or higher as a high-quality result.

**authority** runs from 0 to 4. 3 or higher means a highly authoritative source.

An agent can drop everything below those lines before it spends a single token of context, or a single Fetch call, on it.

## The real wall is speed, not money

Each account gets **5 calls per second** for Search and 5 for Fetch.

That limit is per account, not per key. Ten subagents on one account share the same 5 slots.

Fetch also has a cap per website, so hammering one domain fails sooner.

Over the limit, you get an HTTP 429 error. The docs say to wait and retry on 429, 408 and 5xx errors, and not to blindly retry other 4xx errors.

At these prices, a busy agent fleet hits the rate limit long before it notices the bill.

## Why this matters this month

If you run DeepSeek models through **Claude Code or Codex**, those tools already call Search and Fetch on the server side.

Those calls are free today. Billing starts **November 1, 2026, at midnight Beijing time** (October 31, 16:00 UTC).

That is two weeks to check how many search calls your agent makes per task.

## Takeaway

Search wide once, with content on. Drop low scores. Fetch only what is left. Throttle to 5 calls a second.

How many web searches does your coding agent make on a typical task? Have you ever counted?

## Also this cycle

- [Sphinx](https://sphinx-six-theta.vercel.app/) is a Git hook that blocks a push until you answer a question about what your agent's diff does when things fail.
- [JOSIE-Voice](https://x.com/ActuallyIsaak/status/2111766108524958038) runs a real-time voice agent with tool calling entirely on a consumer Mac, LLM via Ollama.
- A [four-step fine-tuning recipe](https://x.com/TheGlobalMinima/status/2111814971353141481): write the tests, evals and benchmark runners before you train the small model.
- [20 Blender 5.2 skills](https://x.com/hakimieiqbal/status/2111747882843873538) give agents the full 3D pipeline, from modeling to export for Unity, Unreal and Godot.
- Ethan Mollick had Fable 5.1 [turn Borges's short stories into playable 3D pieces](https://x.com/emollick/status/2111700285814940159) from one prompt.
