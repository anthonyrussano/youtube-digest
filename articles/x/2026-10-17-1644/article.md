---
title: "Your coding agent's cache hit rate is the bill nobody reads"
caption: "Agent tip: send the same x-session-id header on every request in a Claude Code, Codex or Cursor conversation so turns stay on one provider and reuse its prompt cache..."
edition: "2026-10-17-1644"
lead_source: "https://vercel.com/changelog/ai-gateway-logs-now-show-session-affinity"
---
Your coding agent sends almost the same prompt on every turn.

The whole conversation so far, plus one new message.

If the provider still has that prompt **in cache**, the turn is cheaper and faster. If not, you pay to read it all again.

Most teams never see which one happened.

Vercel just made it visible, and the fix is **one header**.

## What shipped

Vercel's AI Gateway logs now have [a Sessions view](https://vercel.com/changelog/ai-gateway-logs-now-show-session-affinity).

A **gateway** is the layer between your app and the model providers. It routes each request to a provider that serves the model.

The new view groups requests into **sessions**, one per conversation.

Each row names the client that ran it: **Claude Code, Codex or Cursor**. It shows cost, models, providers, and how much of the input was cached across every turn.

Open a session and you get its **cache hit rate**, duration, and the path: every turn, its model, its timing, and which provider served it.

## Why the provider matters

Here is the overlooked part.

The same model is often served by several providers. A gateway can send turn one to provider A and turn two to provider B.

Provider B has never seen your prompt. **Cache miss.** You pay full price for the whole history again.

Vercel's answer is **session affinity**: each turn goes to the provider that served the one before it, because that provider already holds most of the prompt.

A session that stays on one provider reads more of each prompt from cache.

It is on by default for text and chat requests.

## The one-line fix

By default, Vercel guesses which requests belong together, using a fingerprint of the conversation's opening.

Guesses can be wrong. So tell it.

**Send the same `x-session-id` header on every request in a conversation.** Or the same `sessionId` in `providerOptions.gateway`.

Then filter sessions by client, model, provider or cost.

Single-turn sessions are hidden until you clear the minimum-turns filter, so long agent runs float to the top.

## What to do with it

Sort by cost. Look at the cache hit rate.

A long session with a low hit rate is an agent that keeps paying to reread its own history.

That is a routing problem, not a model problem, and now you can see it.

Even if you don't use Vercel, the lesson carries: **pin a conversation to one provider** and give it a stable session id.

Which of your agents do you think has the worst cache hit rate?

## Also this cycle

- OpenCode says [a breach tied to a large-scale distillation attack hit 1.4% of OpenCode Console users](https://twitter.com/opencode/status/2111516673953935833); it is working with Anthropic, OpenAI and Google. Rotate your keys.
- Google has reportedly [open-sourced Harness², a framework for recursive agent harnessing](https://x.com/dr_cintas/status/2111536299836354864), still unconfirmed by Google itself.
- A Claude Code recipe: [run `/goal` in auto mode with a fast Haiku model judging every turn](https://x.com/mirku21/status/2111562917539622944) while Sonnet builds and Opus signs off. Measure before trusting it overnight.
- More of this edition on the site: [the full roundup](https://anthonyrussano.github.io/youtube-digest/reports/2026-10-17-1644.html).
