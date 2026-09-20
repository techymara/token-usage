#!/usr/bin/env python3
"""Report Claude Code token usage cost from local session logs via ccusage.

Prints:
  - Last 24 hours   (approximated as "today, UTC, to date" -- see note below)
  - Last calendar month
  - Last 3 calendar months
  - To date, daily basis (a day-by-day table going back --lookback-days)

Uses ccusage (https://github.com/ryoppippi/ccusage), a local-first CLI that
reads Claude Code's own session logs (~/.claude/projects/**/*.jsonl) and
requires no Anthropic API key of any kind. Run via `npx`, which fetches it
on first use (needs Node.js and network access once; cached after that).

Because this reads local logs, the numbers only cover usage from whichever
machine this script runs on -- run it wherever your actual Claude Code
sessions happen, not from an unrelated environment.

Note on "last 24 hours": ccusage buckets by full UTC calendar day, so a
true trailing-24-hour window isn't available. This script reports the
current UTC day's cost-to-date instead, which undercounts if it's early
in the UTC day.
"""
import argparse
import datetime as dt
import json
import subprocess
import sys
from decimal import Decimal, ROUND_HALF_UP


def money(amount) -> str:
    return f"${Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}"


def shift_months(first_of_month: dt.date, delta: int) -> dt.date:
    """Return the first of the month `delta` months from `first_of_month`."""
    month_index = first_of_month.month - 1 + delta
    year = first_of_month.year + month_index // 12
    month = month_index % 12 + 1
    return first_of_month.replace(year=year, month=month, day=1)


def run_ccusage(since: dt.date, until: dt.date) -> dict:
    """Run `ccusage daily --json` over [since, until] (both inclusive, UTC)."""
    proc = subprocess.run(
        [
            "npx", "--yes", "ccusage@latest", "daily", "--json",
            "--timezone", "UTC",
            "--since", since.isoformat(),
            "--until", until.isoformat(),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        sys.exit(f"ccusage failed (exit {proc.returncode}): {proc.stderr.strip()}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        sys.exit(f"Could not parse ccusage output as JSON:\n{proc.stdout}\n{proc.stderr}")


def total_cost(report: dict) -> Decimal:
    return Decimal(str(report.get("totals", {}).get("totalCost", 0)))


def build_report(lookback_days: int) -> str:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    today = now.date()
    first_of_this_month = today.replace(day=1)

    lines = []
    lines.append(f"Token usage cost report - generated {now.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append("(source: local Claude Code session logs via ccusage - run this on the machine whose usage you want)")
    lines.append("=" * 60)

    # Last 24 hours (approximated as today-UTC-to-date; see module docstring).
    today_report = run_ccusage(today, today)
    lines.append(
        f"\nLast 24 hours (today, UTC, {today.isoformat()} 00:00 -> now): "
        f"{money(total_cost(today_report))}"
    )
    lines.append(
        "  (approximation: ccusage only buckets by full UTC day; this is "
        "today-so-far, not a rolling 24h window)"
    )

    # Last calendar month
    last_month_start = shift_months(first_of_this_month, -1)
    last_month_end = first_of_this_month - dt.timedelta(days=1)
    lm_report = run_ccusage(last_month_start, last_month_end)
    lines.append(
        f"\nLast calendar month ({last_month_start.strftime('%Y-%m')}): "
        f"{money(total_cost(lm_report))}"
    )

    # Last 3 calendar months (the 3 full months before the current one)
    three_months_start = shift_months(first_of_this_month, -3)
    tm_report = run_ccusage(three_months_start, last_month_end)
    lines.append(
        f"\nLast 3 calendar months ({three_months_start.strftime('%Y-%m')} "
        f"through {last_month_start.strftime('%Y-%m')}): "
        f"{money(total_cost(tm_report))}"
    )

    # To date, daily basis
    lookback_start = today - dt.timedelta(days=lookback_days)
    yesterday = today - dt.timedelta(days=1)
    daily_report = run_ccusage(lookback_start, yesterday)
    lines.append(
        f"\nTo date, daily basis (last {lookback_days} completed UTC days, "
        f"{lookback_start.isoformat()} through {yesterday.isoformat()}):"
    )
    running_total = Decimal(0)
    for day in daily_report.get("daily", []):
        day_cost = Decimal(str(day.get("totalCost", 0)))
        running_total += day_cost
        lines.append(f"  {day['period']}: {money(day_cost)}")
    lines.append(f"  {'-' * 20}")
    lines.append(f"  Total: {money(running_total)}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=365,
        help="how many completed days back to include in the 'to date' daily table (default: 365)",
    )
    args = parser.parse_args()

    print(build_report(args.lookback_days))


if __name__ == "__main__":
    main()
