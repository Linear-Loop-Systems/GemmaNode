# GemmaNode

GemmaNode is a personal AI orchestration system routing coding tasks across free LLMs (Gemini Flash, DeepSeek, Qwen) via a local supervisor and pull-based polling pipeline. Give it a task, close the laptop — it wakes on demand, executes autonomously, and escalates only the hardest problems to Claude. Open source, single-user by design. 

## How It Works

You talk to **Gemma**, a single point of contact that handles prompt engineering, model routing, and task delegation — similar to talking to one bot in a Discord server while it manages others behind the scenes.

```
You → Gemma (local supervisor) → routes task to:
        ├─ Gemini Flash   (UI / layout, ~1,500 req/day free)
        ├─ DeepSeek       (backend coding, hosted on Kaggle GPU)
        ├─ Qwen           (cleanup / verification)
        └─ Claude         (manual escalation for genuinely hard problems)
```

- **Outbound-only pull architecture** — the laptop polls an Azure VM every 5 seconds for new tasks and streams results back over HTTPS. No inbound ports, no exposed firewall rules.
- **Linear Model Handoff** — on failure, a task shuffles to the next model down the priority chain instead of retrying recursively. If every free model strikes out, Gemma writes `HANDOFF_CLAUDE.txt` for manual review.
- **Sleep/Wake on demand** — the laptop wakes via Wake-on-LAN, triggered remotely from the website.
- **Docker-isolated execution** — OpenHands runs in a resource-capped container (`--memory=6g --cpus=3`), and the host-control agent runs under an unprivileged `ai-executor` OS user with zero admin/sudo access.

## Stack

| Priority | Model | Role |
|---|---|---|
| 1 | Gemini Flash | Primary workhorse — UI/layout |
| 2 | DeepSeek (open weights) | Backend coding engine |
| 3 | Qwen (open weights) | Cleanup & verification |
| 4 | Gemma (1.5B/2B local) | Routing/supervisor logic |
| 5 | Claude | Manual escalation only, via web chat |

## Status

Currently in the **Bootstrap stage** — building the minimal working loop (local gateway, polling client, routing prompt, model handoff, core integrations) before handing tasks to the automated Self-Build stage.

## Design Principles

- Entirely free-model stack — no paid APIs required to run
- No Claude API, ever — Claude access is manual copy-paste only
- File/code privacy matters; output privacy doesn't — no code/files sent to third-party hosted commercial inference
- Single-user, website-auth only — no multi-tenant complexity
- Stateless supervisor — zero conversation history, 2048-token context cap, wiped after every routing decision

## Hardware

Runs on a Lenovo ThinkPad T14s (integrated graphics, no dGPU) — local models are kept small (~8B params or under) for usable speed on CPU.

## License

Apache 2.0 — see [LICENSE](LICENSE).

## Contributing

This project is early-stage and evolving fast. Issues and PRs welcome once the Bootstrap stage is complete and the core loop is stable.
