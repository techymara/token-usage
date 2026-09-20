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

For a nightly emailed version of this report, see email_report.py.
"""
import argparse

from ccusage_report import compute_report, money


def build_report(lookback_days: int) -> str:
    r = compute_report(lookback_days)

    lines = []
    lines.append(f"Token usage cost report - generated {r['generated_at'].strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append("(source: local Claude Code session logs via ccusage - run this on the machine whose usage you want)")
    lines.append("=" * 60)

    lines.append(
        f"\nLast 24 hours (today, UTC, {r['today'].isoformat()} 00:00 -> now): "
        f"{money(r['today_cost'])}"
    )
    lines.append(
        "  (approximation: ccusage only buckets by full UTC day; this is "
        "today-so-far, not a rolling 24h window)"
    )

    lines.append(
        f"\nLast calendar month ({r['last_month_start'].strftime('%Y-%m')}): "
        f"{money(r['last_month_cost'])}"
    )

    lines.append(
        f"\nLast 3 calendar months ({r['three_months_start'].strftime('%Y-%m')} "
        f"through {r['last_month_start'].strftime('%Y-%m')}): "
        f"{money(r['three_months_cost'])}"
    )

    lines.append(
        f"\nTo date, daily basis (last {lookback_days} completed UTC days, "
        f"{r['lookback_start'].isoformat()} through {r['lookback_end'].isoformat()}):"
    )
    for period, cost in r["daily"]:
        lines.append(f"  {period}: {money(cost)}")
    lines.append(f"  {'-' * 20}")
    lines.append(f"  Total: {money(r['daily_total'])}")

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
