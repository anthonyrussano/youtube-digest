# Outline (roundup)
Lead: Coinbase's ladder for agent autonomy
1. Hook: most teams treat agent autonomy as an on/off switch. Coinbase uses a ladder.
2. The three rungs: supervised, sampled, exceptions-only. Move up only when measured confidence clears a threshold your policy sets.
3. Which steps qualify: four yes/no questions (checkable, bounded loop, traceable, human fallback).
4. Why: the loop is only as trustworthy as the check. Agents are probabilistic, so you need datasets and repeated evals, not exact matches.
5. What people miss: speed one step up and the bottleneck moves downstream. Watch the whole process, not just the agent.
6. Rule of thumb: deterministic outside, adaptive inside.
Other items (one line each): Bedrock structured outputs; AWS Transform Kafka business case; DiscoveryRSI; Codex CLI/Cloud; Claude Code three-model setup; FastVideo on two DGX Sparks; SageMaker Studio sign-up.
Close: which rung are your agents on, and what check moved them up?
