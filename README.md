<a name="top"></a>
<div align="center">

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:6b46c1,100:2b6cb0&height=120&section=header&text=ORGCHART&fontSize=48&fontColor=ffffff&fontAlignY=58" width="100%" alt="ORGCHART"/>

# ORGCHART

### Org charts and headcount plans generated from CSV / HRIS export

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&duration=3500&pause=1000&color=6B46C1&center=true&vCenter=true&width=720&lines=Org+charts+and+headcount+plans+generated+from+CSV++HRIS+expo;Self-hostable+%C2%B7+MCP-native+%C2%B7+CI-ready+%C2%B7+polyglot" width="720"/>

[![PyPI](https://img.shields.io/pypi/v/cognis-orgchart.svg?color=6b46c1)](https://pypi.org/project/cognis-orgchart/) [![CI](https://github.com/cognis-digital/orgchart/actions/workflows/ci.yml/badge.svg)](https://github.com/cognis-digital/orgchart/actions) [![License: COCL 1.0](https://img.shields.io/badge/License-COCL%201.0-2b6cb0.svg)](LICENSE) [![Suite](https://img.shields.io/badge/Cognis-Neural%20Suite-6b46c1.svg)](https://github.com/cognis-digital)

*Business Operations — run the company without a SaaS bill for every function.*

</div>

```bash
pip install cognis-orgchart
orgchart scan .            # → prioritized findings in seconds
```

## Usage — step by step

`orgchart` builds org charts and headcount plans from a CSV / HRIS export. Every subcommand takes a CSV path (or `-` for stdin).

1. **Install**:
   ```bash
   pip install -e .
   orgchart --version
   ```
2. **Render the reporting tree** from an export:
   ```bash
   orgchart tree employees.csv
   ```
3. **Compute metrics** — per-employee span-of-control and headcount roll-up:
   ```bash
   orgchart metrics employees.csv
   ```
4. **Read the output** as JSON, or pipe via stdin:
   ```bash
   orgchart --format json summary employees.csv | jq .
   cat employees.csv | orgchart tree -
   ```
5. **Automate in CI** — validate structural integrity (cycles, missing managers) on every HRIS sync:
   ```bash
   orgchart validate employees.csv || exit 1
   ```

## Contents

- [Why orgchart?](#why) · [Features](#features) · [Quick start](#quick-start) · [Example](#example) · [Architecture](#architecture) · [AI stack](#ai-stack) · [How it compares](#how-it-compares) · [Integrations](#integrations) · [Install anywhere](#install-anywhere) · [Related](#related) · [Contributing](#contributing)

<a name="why"></a>
## Why orgchart?

ops + people teams

`orgchart` is single-purpose, scriptable, and self-hostable: point it at a target, get prioritized results in the format your workflow already speaks (table · JSON · SARIF), gate CI on it, and let agents drive it over MCP.

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="features"></a>
## Features

- ✅ Parse Csv
- ✅ Build Org
- ✅ Render Tree
- ✅ Load Org From Csv
- ✅ Runs on Linux/macOS/Windows · Docker · devcontainer
- ✅ Ports in Python, JavaScript, Go, and Rust (`ports/`)

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="quick-start"></a>
## Quick start

```bash
pip install cognis-orgchart
orgchart --version
orgchart scan .                       # scan current project
orgchart scan . --format json         # machine-readable
orgchart scan . --fail-on high        # CI gate (non-zero exit)
```

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="example"></a>
## Example

```text
$ orgchart scan .
  [HIGH    ] ORG-001  example finding             (./src/app.py)
  [MEDIUM  ] ORG-002  another signal              (./config.yaml)

  2 findings · risk score 5 · 38ms
```

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="architecture"></a>
## Architecture

```mermaid
flowchart LR
  IN[capture / scan] --> P[orgchart<br/>parse + map]
  P --> OUT[report]
```

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="ai-stack"></a>
## Use it from any AI stack

`orgchart` is interoperable with every popular way of using AI:

- **MCP server** — `orgchart mcp` (Claude Desktop, Cursor, Cognis.Studio, [uncensored-fleet](https://github.com/cognis-digital/uncensored-fleet))
- **OpenAI-compatible / JSON** — pipe `orgchart scan . --format json` into any agent or LLM
- **LangChain · CrewAI · AutoGen · LlamaIndex** — wrap the CLI/JSON as a tool in one line
- **CI / scripts** — exit codes + SARIF for non-AI pipelines

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="how-it-compares"></a>
## How it compares

| | **Cognis orgchart** | OrgChart |
|---|:---:|:---:|
| Self-hostable, no account | ✅ | varies |
| Single command, zero config | ✅ | ⚠️ |
| JSON + SARIF for CI | ✅ | varies |
| MCP-native (AI agents) | ✅ | ❌ |
| Polyglot ports (JS/Go/Rust) | ✅ | ❌ |
| Open license | ✅ COCL | varies |

*Built in the spirit of **OrgChart**, re-framed the Cognis way. Missing a credit? Open a PR.*

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="integrations"></a>
## Integrations

Pipes into your stack: **SARIF** for code-scanning, **JSON** for anything, an **MCP server** (`orgchart mcp`) for AI agents, and a webhook forwarder for SIEM/Slack/Jira. See [`docs/INTEGRATIONS.md`](docs/INTEGRATIONS.md).

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="install-anywhere"></a>
## Install — every way, every platform

```bash
pip install "git+https://github.com/cognis-digital/orgchart.git"    # pip (works today)
pipx install "git+https://github.com/cognis-digital/orgchart.git"   # isolated CLI
uv tool install "git+https://github.com/cognis-digital/orgchart.git" # uv
pip install cognis-orgchart                                          # PyPI (when published)
docker run --rm ghcr.io/cognis-digital/orgchart:latest --help        # Docker
brew install cognis-digital/tap/orgchart                             # Homebrew tap
curl -fsSL https://raw.githubusercontent.com/cognis-digital/orgchart/main/install.sh | sh
```

| Linux | macOS | Windows | Docker | Cloud |
|---|---|---|---|---|
| `scripts/setup-linux.sh` | `scripts/setup-macos.sh` | `scripts/setup-windows.ps1` | `docker run ghcr.io/cognis-digital/orgchart` | [DEPLOY.md](docs/DEPLOY.md) (AWS/Azure/GCP/k8s) |

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="related"></a>
## Related Cognis tools

- [`invoctl`](https://github.com/cognis-digital/invoctl) — CLI invoicing + payment-link generator with PDF and a local ledger
- [`churnlens`](https://github.com/cognis-digital/churnlens) — Self-hosted SaaS metrics — MRR, churn, LTV from Stripe or CSV
- [`leadforge`](https://github.com/cognis-digital/leadforge) — Lightweight MCP-native CRM pipeline with email sequences
- [`quotecraft`](https://github.com/cognis-digital/quotecraft) — Proposal / quote / SOW generator — YAML to branded PDF
- [`boardroom`](https://github.com/cognis-digital/boardroom) — Investor-update and KPI one-pager generator from your metrics
- [`seataudit`](https://github.com/cognis-digital/seataudit) — SaaS license, seat-usage and shadow-IT auditor

**Explore the suite →** [🗂️ all 170+ tools](https://github.com/cognis-digital/cognis-neural-suite) · [⭐ awesome-cognis](https://github.com/cognis-digital/awesome-cognis) · [🔗 cognis-sources](https://github.com/cognis-digital/cognis-sources) · [🤖 uncensored-fleet](https://github.com/cognis-digital/uncensored-fleet) · [🧠 engram](https://github.com/cognis-digital/engram)

<div align="right"><a href="#top">↑ back to top</a></div>

<a name="contributing"></a>
## Contributing

PRs, new rules, and demo scenarios are welcome under the collaboration-pull model — see [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

> ### ⭐ If `orgchart` saved you time, **star it** — it genuinely helps others find it.

## Interoperability

`{}` composes with the 300+ tool Cognis suite — JSON in/out and a shared
OpenAI-compatible `/v1` backbone. See **[INTEROP.md](INTEROP.md)** for the
suite map, composition patterns, and reference stacks.

## License

Source-available under the **Cognis Open Collaboration License (COCL) v1.0** — free for personal, internal-evaluation, research, and educational use; **commercial / production use requires a license** (licensing@cognis.digital). See [LICENSE](LICENSE).

---

<div align="center"><sub><b><a href="https://cognis.digital">Cognis Digital</a></b> · one of 170+ tools in the <a href="https://github.com/cognis-digital/cognis-neural-suite">Cognis Neural Suite</a> · <i>Making Tomorrow Better Today</i></sub></div>
