# token-usage

Local Claude Code cost reports (24h / month / 3 months / daily) — no API key needed.

## How this works

`scripts/report_cost.py` shells out to [ccusage](https://github.com/ryoppippi/ccusage),
a local-first CLI that reads Claude Code's own session logs
(`~/.claude/projects/**/*.jsonl`) and needs no Anthropic API key at all. It prints:

- Last 24 hours (approximated as "today, UTC, so far" -- ccusage only
  buckets by full UTC calendar day, so a true rolling 24h window isn't
  available; see the note in the script's docstring)
- Last calendar month
- Last 3 calendar months
- A day-by-day cost table "to date" (defaults to the trailing 365 days;
  override with `--lookback-days`)

Anthropic's Admin API (`/v1/organizations/cost_report`) was the original
approach here, but it requires an Admin API key scoped with organization
cost/usage-report permissions -- which isn't obtainable for every account
type (e.g. an Individual org may get a `permission_error` from Anthropic
regardless of key scope). Reading local session logs sidesteps that
entirely, at the cost of only seeing usage from wherever it's run.

### Setup (one-time)

1. Make sure Node.js is available (for `npx`) -- ccusage is fetched
   on demand, no separate install step needed.
2. There's no Python dependency to install anymore; `requirements.txt` is
   kept empty for now in case one is needed later.

### Running it

**Run this on the machine where your Claude Code sessions actually happen**
(e.g. your laptop) -- not from an unrelated environment, since the report
only reflects whatever `~/.claude/projects/` it finds locally.

```bash
python3 scripts/report_cost.py
# or, for a longer daily history:
python3 scripts/report_cost.py --lookback-days 730
```

Each run re-parses the local session logs live -- no separate data files
are kept, since ccusage reads directly from Claude Code's own logs.
