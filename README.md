# GemmaNode

**AI compute orchestration, without locking you into one model, one machine, or one provider.**

GemmaNode is an open-source AI compute orchestration network. It coordinates AI models, autonomous agents, local hardware, cloud compute, and external AI providers through a single, unified layer — so you talk to one system, and it figures out which resource is best suited to handle each part of the work.

🔗 **Website:** [gemmanode.vighnesh.me](https://gemmanode.vighnesh.me/)

---

## Why GemmaNode

Modern AI workflows span multiple tools — a model for reasoning, an agent for implementation, cloud compute for heavier jobs, and occasionally a stronger model for the hardest problems. Wiring these together manually means constant context-switching between dashboards, notebooks, and consoles.

GemmaNode puts a single orchestrator in front of a broad resource pool, so you don't have to.

## How it works

At a high level, a task moves through the same general path every time:

1. **You submit a task** — via the web app, desktop client, mobile client, or API/CLI.
2. **GemmaNode analyzes the task** — reviewing its general nature (coding, research, generation, analysis, etc.).
3. **Available resources are considered** — from local hardware, cloud compute, AI providers, and agent frameworks.
4. **Work is assigned to a suitable resource** — based on general factors like capability, availability, and cost.
5. **Independent work can run concurrently** — when resources allow, multiple agents or parts of a task execute in parallel.
6. **Results come back to you** — collected, consolidated, and returned through your originating client.

Difficult, failing, or uncertain tasks can optionally be escalated for manual review by a stronger model, rather than being forced through an automated path that isn't working.

> The specifics of task analysis and resource selection are intentionally not detailed here — this document describes what happens, not how it's computed internally.

## Resource pool

GemmaNode is designed to work with a broad, extensible pool of resources. Availability, quotas, and pricing for any third-party resource are set by that provider and can change — nothing here is a permanent guarantee.

| Category | Examples | General purpose |
|---|---|---|
| Local Compute | Your own PC | Private, low-latency execution |
| Cloud Compute | Camber, Kaggle, Google Colab, Hugging Face | Additional compute/inference capacity |
| AI Providers | Gemini API, OpenRouter, Pollinations AI | External model capabilities |
| Agents | OpenHands, OpenClaw, Hermes | Autonomous, multi-step execution |
| Manual Escalation | Claude | Human-reviewed handling of complex/uncertain tasks |

No single provider is a hard dependency — resources can be added, removed, or swapped without changing how you interact with GemmaNode.

## Design principles

- **Unified interface** — one point of contact regardless of which resource performs the work.
- **Provider independence** — no single vendor or model is a hard dependency.
- **Escalation, not lock-in** — when automated resources can't confidently resolve a task, it can be escalated manually instead of failing silently.
- **Free-tier aware** — built to make good use of free and user-controlled resources, without promising unlimited free compute forever.
- **Local by default, external when you choose** — data only leaves your machine when a task is routed to an external provider you've configured.
- **Open development** — developed in the open, with an intent to remain free for personal and hobbyist use.

## Project status

GemmaNode is under active development. This is an honest snapshot, not a roadmap promise.

**Current**
- Local orchestration on your own hardware
- Coordination across multiple free/open AI models
- BYOK-based provider configuration
- Open-source codebase

**Experimental**
- Cloud/remote compute integrations
- Autonomous agent framework support
- Parallel multi-agent task execution
- Remote wake/resume of queued tasks

**Planned**
- Broader provider & agent marketplace
- Packaged installer distribution
- Expanded monitoring & task history UI
- Public documentation site

## Requirements

- A supported OS (Windows primary; see docs for other platforms as they're added)
- A dedicated GPU is optional — CPU inference is supported
- A local model runtime (e.g. Ollama) if you want on-device models
- Internet access for any external provider or cloud resource you choose to connect
- Your own API keys/accounts for any external provider you want to use (BYOK — nothing is shared or hardcoded)

Exact setup steps live in the docs (link coming soon) rather than here, since they change as the project evolves.

## Privacy

- **Local resources** — when a task runs on your own hardware, your code and files can stay on your machine according to how you've configured GemmaNode.
- **External providers** — when a task is sent to an external AI provider or cloud resource, the relevant data leaves your machine and is subject to that provider's own service and terms.

No privacy guarantees are made beyond what your actual configuration provides.

## Contributing

This project is early-stage and evolving. Issues and PRs are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).

## Disclosure

To protect the project's evolving implementation, this README intentionally omits private routing logic, scheduling algorithms, infrastructure details, credentials, internal configuration, and unreleased implementation details. Provider names mentioned (Gemini API, OpenRouter, Pollinations AI, Camber, Kaggle, Google Colab, Hugging Face, OpenHands, OpenClaw, Hermes, Claude) refer to their own respective services and are not affiliated with or endorsed by this project. Availability, pricing, and quotas are determined by each provider and may change.
