# GemmaNode

GemmaNode is a personal AI orchestration system that routes coding tasks across free LLMs via a local supervisor. Give it a task, close the laptop — it wakes on demand, executes autonomously, and escalates only the hardest problems to Claude. Open source, single-user by design.

## How It Works

You talk to **Gemma**, a single point of contact that handles prompt engineering, model routing, and task delegation — similar to talking to one bot in a Discord server while it manages others behind the scenes.

```
You → Gemma (local supervisor) → routes task to the best available free model,
       with harder problems escalated to Claude for manual review
```

- **Outbound-only architecture** — the laptop reaches out to a remote task queue on its own schedule and streams results back over HTTPS. No inbound ports, no exposed firewall rules.
- **Automatic model handoff** — on failure, a task moves to the next available model instead of retrying the same one indefinitely. If every free model strikes out, Gemma prepares a summary for manual review.
- **Sleep/Wake on demand** — the laptop wakes remotely, triggered from the website.
- **Sandboxed execution** — task execution runs in a resource-capped container, with the host-control agent isolated under a restricted, non-admin account.

## Stack

Free/open-weight models handle the bulk of tasks, routed by a small local supervisor model. Claude is used only as a manual, opt-in escalation path for problems the free stack can't resolve — never called via API.

## Status

Currently in the **Bootstrap stage** — building the minimal working loop (local gateway, task polling, routing logic, model handoff, core integrations) before handing tasks to the automated Self-Build stage.

## Minimum Requirements

- **OS:** Linux or macOS recommended (Windows via WSL2)
- **Python:** 3.8+ (isolated venv required)
- **RAM:** 16 GB minimum
- **CPU:** No dedicated GPU required — local models are kept small enough for CPU-usable speed
- **Docker:** Required, with resource limits enforced
- **Node.js:** Required for the background agent daemon
- **Accounts/keys needed:**
  - Google Gemini API key (free tier)
  - A GPU-hosting account for open-weight model inference (free tier)
  - An always-on host for the task queue backend
  - Claude account (free plan is sufficient — no API key needed, manual escalation only)
- **Network:** Outbound HTTPS only — no port-forwarding or inbound firewall rules needed

## Design Principles

- Entirely free-model stack — no paid APIs required to run
- No Claude API, ever — Claude access is manual copy-paste only
- File/code privacy matters; output privacy doesn't — no code/files sent to third-party hosted commercial inference
- Single-user, website-auth only — no multi-tenant complexity
- Stateless supervisor — no persistent conversation history retained by the routing layer

## Hardware

Tuned to run on a modest laptop with integrated graphics — no dedicated GPU required. Local models are kept small enough for usable CPU speed.

## License

Apache 2.0 — see [LICENSE](https://github.com/Linear-Loop-Systems/GemmaNode/blob/main/LICENSE).

## Contributing

This project is early-stage and evolving fast. Issues and PRs welcome once the Bootstrap stage is complete and the core loop is stable.
