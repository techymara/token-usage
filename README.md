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

## Scheduling (nightly email, macOS)

`scripts/email_report.py` emails a clean HTML version of the report (a
summary table + a daily breakdown table, with the headline numbers in the
subject line) instead of printing to the terminal. It reuses the same
ccusage-backed logic as `report_cost.py` via `scripts/ccusage_report.py`.

It also supports skip/reschedule controls sent right from the email: each
one includes buttons to skip tomorrow's report, skip the next 7 days, or
set an exact date for the next report. Clicking a button opens a pre-filled
reply; the next scheduled run checks for that reply (over IMAP, unread
mail only) before sending, and skips itself if asked to.

### One-time setup

1. Generate a Gmail **App Password** (not your regular password) at
   <https://myaccount.google.com/apppasswords> -- requires 2-Step
   Verification to be turned on for the account.
2. In Gmail, make sure IMAP is enabled: **Settings -> Forwarding and
   POP/IMAP -> Enable IMAP**. (Needed for the skip/reschedule replies to
   be read back; regular sending works without it.)
3. Create `~/.token-usage.env` (outside the repo -- never commit
   credentials) with:

   ```bash
   export TOKEN_USAGE_GMAIL_ADDRESS="you@gmail.com"
   export TOKEN_USAGE_GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
   export TOKEN_USAGE_EMAIL_TO="you@gmail.com"   # optional; defaults to the address above
   ```

   Then lock it down: `chmod 600 ~/.token-usage.env`.
4. Test it manually first:

   ```bash
   source ~/.token-usage.env
   python3 scripts/email_report.py
   ```

### Installing the nightly job (7:30 PM daily)

`scheduling/com.maramellstrom.token-usage-report.plist` is a `launchd`
job pre-configured for 7:30 PM every night. It assumes this repo is
cloned to `~/token-usage` -- edit the `cd` path inside the plist first if
yours lives elsewhere.

```bash
cp scheduling/com.maramellstrom.token-usage-report.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.maramellstrom.token-usage-report.plist
```

To run it immediately (without waiting for 7:30 PM) to confirm it works:

```bash
launchctl start com.maramellstrom.token-usage-report
```

Output (including any error output, if something goes wrong) is appended
to `~/token-usage-report.log`; separate `launchd`-level diagnostics land in
`/tmp/token-usage-report.launchd.{out,err}.log`.

To stop the schedule:

```bash
launchctl unload ~/Library/LaunchAgents/com.maramellstrom.token-usage-report.plist
```
