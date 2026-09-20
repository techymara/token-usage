# token-usage

Scheduled task: review my token usage and tell me the cost for each from the last 24 hours, last calendar month, last calendar 3 months, and to date on a daily basis.

## How this works

`scripts/report_cost.py` calls Anthropic's [Usage & Cost Admin API](https://platform.claude.com/docs/en/manage-claude/usage-cost-api)
(`/v1/organizations/cost_report`) and prints:

- Last 24 hours (approximated as "today, UTC, so far" -- the Cost API only
  buckets by full UTC calendar day, so a true rolling 24h window isn't
  available; see the note in the script's docstring)
- Last calendar month
- Last 3 calendar months
- A day-by-day cost table "to date" (defaults to the trailing 365 days;
  override with `--lookback-days`)

### Setup (one-time)

1. In the [Claude Console](https://console.claude.com/), create an **Admin API key**
   (`sk-ant-admin...`) under Settings > Admin keys. This requires an org admin/owner.
   A regular workspace API key will *not* work against this endpoint.
2. Add it as a secret environment variable on this environment named
   `ANTHROPIC_ADMIN_KEY` (Claude Code on the web: environment settings > secrets).
3. Install the one dependency: `pip install -r requirements.txt`.

### Running it

```bash
python3 scripts/report_cost.py
# or, for a longer daily history:
python3 scripts/report_cost.py --lookback-days 730
```

Each scheduled run of this task re-executes the script live against the
Admin API -- no local data files are kept, since Anthropic retains the full
history server-side.
