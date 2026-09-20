"""Shared helpers for querying ccusage and computing the four-window cost report.

Used by both report_cost.py (plain-text CLI report) and email_report.py
(HTML email). See report_cost.py's module docstring for the ccusage
background and caveats (UTC-day bucketing, local-only data).
"""
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


def compute_report(lookback_days: int) -> dict:
    """Run ccusage for all four windows; return raw figures (Decimals/dates)."""
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    today = now.date()
    first_of_this_month = today.replace(day=1)

    today_cost = total_cost(run_ccusage(today, today))

    last_month_start = shift_months(first_of_this_month, -1)
    last_month_end = first_of_this_month - dt.timedelta(days=1)
    last_month_cost = total_cost(run_ccusage(last_month_start, last_month_end))

    three_months_start = shift_months(first_of_this_month, -3)
    three_months_cost = total_cost(run_ccusage(three_months_start, last_month_end))

    lookback_start = today - dt.timedelta(days=lookback_days)
    yesterday = today - dt.timedelta(days=1)
    daily_report = run_ccusage(lookback_start, yesterday)
    daily = [
        (day["period"], Decimal(str(day.get("totalCost", 0))))
        for day in daily_report.get("daily", [])
    ]
    daily_total = sum((cost for _, cost in daily), Decimal(0))

    return {
        "generated_at": now,
        "today": today,
        "today_cost": today_cost,
        "last_month_start": last_month_start,
        "last_month_cost": last_month_cost,
        "three_months_start": three_months_start,
        "three_months_cost": three_months_cost,
        "lookback_start": lookback_start,
        "lookback_end": yesterday,
        "daily": daily,
        "daily_total": daily_total,
    }
