#!/usr/bin/env python3
"""Report Anthropic API cost for this org via the Admin Cost Report API.

Prints:
  - Last 24 hours   (approximated as "today, UTC, to date" -- see note below)
  - Last calendar month
  - Last 3 calendar months
  - To date, daily basis (a day-by-day table going back --lookback-days)

Requires an Admin API key (sk-ant-admin...) in ANTHROPIC_ADMIN_KEY (or
ANTHROPIC_API_KEY). Regular workspace API keys cannot call this endpoint.

Note on "last 24 hours": the Cost Report API only buckets by full UTC
calendar day (bucket_width=1d), so a true trailing-24-hour window isn't
available. This script reports the current UTC day's cost-to-date instead,
which undercounts if it's early in the UTC day. For a precise trailing
24-hour token count (not cost), use the Usage Report API's 1h buckets.
"""
import argparse
import datetime as dt
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

import requests

API_URL = "https://api.anthropic.com/v1/organizations/cost_report"
ANTHROPIC_VERSION = "2023-06-01"
CENTS_PER_UNIT = Decimal(100)


def get_api_key() -> str:
    key = os.environ.get("ANTHROPIC_ADMIN_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.exit(
            "Missing ANTHROPIC_ADMIN_KEY (or ANTHROPIC_API_KEY) environment variable.\n"
            "Create an Admin API key in the Claude Console "
            "(Settings > Admin keys) and set it as a secret on this "
            "environment, then re-run."
        )
    return key


def fmt(ts: dt.datetime) -> str:
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_cost_buckets(starting_at: dt.datetime, ending_at: dt.datetime, api_key: str):
    """Fetch all daily cost buckets in [starting_at, ending_at), paging as needed."""
    buckets = []
    page = None
    for _ in range(200):  # safety cap: 200 pages * 31 days/page ~ 17 years
        params = {
            "starting_at": fmt(starting_at),
            "ending_at": fmt(ending_at),
            "bucket_width": "1d",
            "limit": 31,
        }
        if page:
            params["page"] = page
        resp = requests.get(
            API_URL,
            params=params,
            headers={"anthropic-version": ANTHROPIC_VERSION, "x-api-key": api_key},
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()
        buckets.extend(body["data"])
        if not body.get("has_more"):
            break
        page = body["next_page"]
    return buckets


def bucket_total_usd(bucket: dict) -> Decimal:
    return sum((Decimal(r["amount"]) for r in bucket["results"]), Decimal(0)) / CENTS_PER_UNIT


def money(amount: Decimal) -> str:
    return f"${amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}"


def shift_months(first_of_month: dt.date, delta: int) -> dt.date:
    """Return the first of the month `delta` months from `first_of_month`."""
    month_index = first_of_month.month - 1 + delta
    year = first_of_month.year + month_index // 12
    month = month_index % 12 + 1
    return first_of_month.replace(year=year, month=month, day=1)


def as_utc_midnight(d: dt.date) -> dt.datetime:
    return dt.datetime.combine(d, dt.time.min, tzinfo=dt.timezone.utc)


def build_report(api_key: str, lookback_days: int) -> str:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    today = now.date()
    today_start = as_utc_midnight(today)
    first_of_this_month = today.replace(day=1)

    lines = []
    lines.append(f"Token usage cost report - generated {fmt(now)}")
    lines.append("=" * 60)

    # Last 24 hours (approximated as today-UTC-to-date; see module docstring).
    # ending_at must be tomorrow's midnight, not "now": the API only returns
    # buckets whose end is <= ending_at, so passing "now" (which is before
    # today's bucket officially "ends") would exclude today's data entirely.
    today_buckets = fetch_cost_buckets(
        today_start, today_start + dt.timedelta(days=1), api_key
    )
    today_total = sum((bucket_total_usd(b) for b in today_buckets), Decimal(0))
    lines.append(
        f"\nLast 24 hours (today, UTC, {today.isoformat()} 00:00 -> now): "
        f"{money(today_total)}"
    )
    lines.append(
        "  (approximation: Cost API only buckets by full UTC day; this is "
        "today-so-far, not a rolling 24h window)"
    )

    # Last calendar month
    last_month_start = shift_months(first_of_this_month, -1)
    lm_buckets = fetch_cost_buckets(
        as_utc_midnight(last_month_start), as_utc_midnight(first_of_this_month), api_key
    )
    last_month_total = sum((bucket_total_usd(b) for b in lm_buckets), Decimal(0))
    lines.append(
        f"\nLast calendar month ({last_month_start.strftime('%Y-%m')}): "
        f"{money(last_month_total)}"
    )

    # Last 3 calendar months (the 3 full months before the current one)
    three_months_start = shift_months(first_of_this_month, -3)
    tm_buckets = fetch_cost_buckets(
        as_utc_midnight(three_months_start), as_utc_midnight(first_of_this_month), api_key
    )
    three_month_total = sum((bucket_total_usd(b) for b in tm_buckets), Decimal(0))
    lines.append(
        f"\nLast 3 calendar months ({three_months_start.strftime('%Y-%m')} "
        f"through {shift_months(first_of_this_month, -1).strftime('%Y-%m')}): "
        f"{money(three_month_total)}"
    )

    # To date, daily basis
    lookback_start = today - dt.timedelta(days=lookback_days)
    all_buckets = fetch_cost_buckets(as_utc_midnight(lookback_start), today_start, api_key)
    lines.append(
        f"\nTo date, daily basis (last {lookback_days} completed UTC days, "
        f"{lookback_start.isoformat()} through {(today - dt.timedelta(days=1)).isoformat()}):"
    )
    running_total = Decimal(0)
    for bucket in all_buckets:
        day = bucket["starting_at"][:10]
        day_total = bucket_total_usd(bucket)
        running_total += day_total
        lines.append(f"  {day}: {money(day_total)}")
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

    api_key = get_api_key()
    print(build_report(api_key, args.lookback_days))


if __name__ == "__main__":
    main()
