# Final check: 2026-10-23-1704

- Research: lead facts come from OpenAI's post "Securing our frontier model training environment" and OpenAI's announcement post (DNS misconfiguration on Sept 20; RL resumed Oct 1; offline world; containers inside microVMs; three red-team goals; hundreds of billions of tokens; Kata CVE-2026-24834, gVisor fd handling, Moby/Docker syscall filters, three kernel CVEs; exits through metrics, logging and auth; reused firewall-approved connection; covert channels via CPU cache timing, shared storage, CPU contention, TLS cert cache; "acoustic modem-like signal"; findings declined; red-teaming in safety cases). Rauch's post for noisy-neighbor and dedicated hardware.
- Changed: the upcoming model's name is left out ("its upcoming cyber model"); kernel CVE numbers listed as "three Linux kernel CVEs"; the checklist items are framed as takeaways, not OpenAI's own advice, and "Deny DNS by default" is tied to how the incident began. Vercel Sandbox claims from Rauch's post are omitted as promotional.
- Caveats: OpenAI doesn't say which cloud or hypervisor runs the microVMs beyond the patched projects.
- Title names the idea. Caption is tip-first (Kata, gVisor or Docker), ends in "...", no "$" plus number, no "Mind Blow". Body has no "Mind Blow".
- Roundup shape: lead in short sections, six one-line Also-this-cycle bullets from this edition, closing question that invites replies.
- Images: one video frame from "Inside Arca's Long-Horizon Agents That Run the Business" (AI Engineer, Aman Singh, YouTube), slide fills the frame, speaker inset only, credited in alt text, placed after the bullet linking the timestamped video.
  - video-frame /workspace/2026-10-23-1704-1-arca.png, source https://www.youtube.com/watch?v=oP2WLFpMoDY&t=660s (slide "Agents drive the firm's work"; text link t=660)
- Not posted in this run: queued for the next X Article posting slot (Saturday 9:30 AM PT).
