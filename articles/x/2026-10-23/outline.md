# Outline (roundup)
Lead (overlooked angle, plain language):
1. Hook: Claude proved 239 entry points in 123 libraries can't crash. Everyone quoted the counts. The useful part is what decides what gets proven: your fuzz target.
2. What happened, briefly: binaries, Rocq, 180M lines, typical 600k-line proof, real bugs (20 MB OOB write, libexpat CVE rediscovery).
3. The missed idea: a statement covers only what the harness checks. No-crash by default; add `if (decompress(compress(x)) != x) abort();` and the no-crash proof becomes a round-trip proof for every input under 64 MiB.
4. Two traps: assert() vanishes under NDEBUG; return -1 counts as a pass (and return 1 makes the statement false). Diagram here.
5. Why it matters: proofs beat tests (7 injected bugs: 5 survived random tests, 7 broke the proof); cost is falling (Opus 5.5 ~40% fewer tokens). Enrollment via AGENTS.md, private findings, no disclosure deadline.
6. Takeaway: audit harnesses now: abort() for every property you care about.
Also this cycle (one line each): Firecrawl hidden-instruction demo (frame), Jarmak harness ranking flip (frame), Shankar data agents, Capitella model backdoors, MuTRAP robot triggers, Conrad credit wall, ThinkingBox consistency, AWS Continuum GA, Quest breach + kill static credentials.
Close: question about which property readers would put in their harness first.
