# auto-multi-agent-logistics

Agentic **read-only** shipping workflow using Python and [CrewAI](https://docs.crewai.com/). You send a natural-language instruction on the CLI; a sequential three-agent crew plans the work, calls allowlisted mock shipping tools, and prints a markdown execution report.

## Features

- **Planner → analyst → reporter** crew (`Process.sequential`)
- **Mock shipping store** (SQLite): rates, tracking, shipment list
- **Safe data access**: no free-form SQL; tools call a parameterized repository only
- **Read-only tools**: rates, tracking, list shipments (no label creation or writes)
- **Execution report**: instruction, plan, tool evidence, findings, hypothetical next actions, gaps

## Requirements

- Python 3.10–3.13
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- `OPENAI_API_KEY` for live crew runs (unit tests do not need it)

## Setup

```bash
cd auto-multi-agent-logistics
uv venv
uv pip install --system-certs -e ".[dev]"   # use --system-certs if uv hits TLS errors
cp .env.example .env
# Edit .env and set OPENAI_API_KEY
```

## Usage

```bash
uv run logistics-crew "What's the cheapest mock rate from 01310-000 to 22041-080 for 2.5 kg, and where is tracking BR123456789BR?"
```

Options:

- `-o, --output PATH` — also write the report to a file
- `-v, --verbose` — verbose CrewAI logging
- `--db PATH` — SQLite mock database (default: `data/shipping.db`, created on first run)

## Mock data

Seed CEPs and tracking IDs include:

| CEP pair | Services |
|----------|----------|
| 01310-000 → 22041-080 | PAC, SEDEX |
| 01310-000 → 30130-000 | PAC, SEDEX |

Tracking examples: `BR123456789BR` (in transit), `BR987654321BR` (delivered).

## Safety model

- Agents cannot run arbitrary SQL or HTTP; they only invoke `get_shipping_rates`, `get_shipment_tracking`, and `list_shipments`.
- Inputs are validated (CEP format, weight &gt; 0, tracking id pattern `BR#########BR`).
- Recommended actions in the report are explicitly **hypothetical** (read-only mode).

## Tests

```bash
.venv/bin/pytest tests/ -m "not integration"
```

End-to-end crew test (requires API key):

```bash
.venv/bin/pytest tests/test_integration_crew.py -m integration
```

## Project layout

```
src/logistics_crew/
  cli.py              # Typer entry via typer.run
  crew.py             # CrewAI agents and tasks
  runner.py           # kickoff + report assembly
  shipping/           # repository, seed, tools, validators
  reporting/          # RunTrace model and markdown renderer
tests/
data/                 # shipping.db created at runtime
```

## License

MIT — see [LICENSE](LICENSE).
