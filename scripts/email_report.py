#!/usr/bin/env python3
"""Email a clean HTML cost report, with headline stats in the subject line,
built from local Claude Code session logs via ccusage (see ccusage_report.py
-- no Anthropic API key needed).

Sends over Gmail SMTP using an App Password (not your regular Gmail
password). Requires these environment variables to be set before running:

  TOKEN_USAGE_GMAIL_ADDRESS       the Gmail address to send from (and to
                                   poll for reply commands, see below)
  TOKEN_USAGE_GMAIL_APP_PASSWORD  an App Password for that address --
                                   generate one at
                                   https://myaccount.google.com/apppasswords
                                   (also needs IMAP enabled: Gmail Settings ->
                                   Forwarding and POP/IMAP -> Enable IMAP)
  TOKEN_USAGE_EMAIL_TO             recipient address (optional; defaults to
                                   TOKEN_USAGE_GMAIL_ADDRESS, i.e. emails
                                   yourself)

Each email includes reply-to-skip/reschedule controls: clicking one opens a
pre-filled reply to TOKEN_USAGE_GMAIL_ADDRESS with a special subject. The
next run scans that inbox (over IMAP, unread mail only) for those subjects
before sending, applies whichever is most restrictive, marks the message
read, and persists the result to ~/.token-usage-schedule-state.json. If
today falls within the resulting skip window, that run sends nothing.

See README.md -> Scheduling for one-time setup and a launchd job that runs
this nightly.
"""
import argparse
import datetime as dt
import email as email_lib
import html
import imaplib
import json
import os
import re
import smtplib
import sys
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ccusage_report import compute_report, money

DEFAULT_DAILY_DAYS = 14
STATE_FILE = os.path.expanduser("~/.token-usage-schedule-state.json")
CMD_TAG = "TOKEN-USAGE-CMD"
CMD_PATTERN = re.compile(
    rf"{re.escape(CMD_TAG)}:\s*(SKIP-TOMORROW|SKIP-7-DAYS|NEXT-ON\s+(\d{{4}}-\d{{2}}-\d{{2}}))",
    re.IGNORECASE,
)


def get_credentials():
    from_addr = os.environ.get("TOKEN_USAGE_GMAIL_ADDRESS")
    app_password = os.environ.get("TOKEN_USAGE_GMAIL_APP_PASSWORD")
    if not from_addr or not app_password:
        sys.exit(
            "Missing TOKEN_USAGE_GMAIL_ADDRESS / TOKEN_USAGE_GMAIL_APP_PASSWORD.\n"
            "Set these (e.g. in ~/.token-usage.env -- see README.md -> Scheduling).\n"
            "The app password comes from https://myaccount.google.com/apppasswords, "
            "not your regular Gmail password."
        )
    to_addr = os.environ.get("TOKEN_USAGE_EMAIL_TO", from_addr)
    return from_addr, app_password, to_addr


# --- Skip/reschedule state -------------------------------------------------

def load_state() -> dict:
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def parse_skip_until(state: dict):
    raw = state.get("skip_until")
    if not raw:
        return None
    try:
        return dt.date.fromisoformat(raw)
    except ValueError:
        return None


def apply_inbox_commands(from_addr: str, app_password: str, today: dt.date, state: dict) -> dict:
    """Fold any unread reply commands into `state` and mark them read.

    Failures here (IMAP down, not enabled, network hiccup) must never block
    sending the report -- they're swallowed and today's send proceeds as if
    no commands were found.
    """
    try:
        conn = imaplib.IMAP4_SSL("imap.gmail.com")
        conn.login(from_addr, app_password)
        conn.select("INBOX")
        status, data = conn.search(None, "UNSEEN", "SUBJECT", f'"{CMD_TAG}"')
        if status == "OK":
            for msg_id in data[0].split():
                status, msg_data = conn.fetch(msg_id, "(RFC822)")
                if status != "OK" or not msg_data or not msg_data[0]:
                    continue
                msg = email_lib.message_from_bytes(msg_data[0][1])
                match = CMD_PATTERN.search(msg.get("Subject", ""))
                if not match:
                    continue
                command = match.group(1).upper()
                if command.startswith("SKIP-TOMORROW"):
                    new_skip = today + dt.timedelta(days=1)
                elif command.startswith("SKIP-7-DAYS"):
                    new_skip = today + dt.timedelta(days=7)
                else:  # NEXT-ON <date>
                    target = dt.date.fromisoformat(match.group(2))
                    new_skip = target - dt.timedelta(days=1)
                current = parse_skip_until(state)
                if current is None or new_skip > current:
                    state["skip_until"] = new_skip.isoformat()
                conn.store(msg_id, "+FLAGS", "\\Seen")
        conn.logout()
    except (imaplib.IMAP4.error, OSError):
        pass
    return state


# --- Email content -----------------------------------------------------

def build_subject(r) -> str:
    return (
        f"Claude Code cost - today {money(r['today_cost'])} | "
        f"last month {money(r['last_month_cost'])} | "
        f"last 3mo {money(r['three_months_cost'])}"
    )


def _mailto(to_addr: str, subject: str, body: str = "") -> str:
    params = {"subject": subject}
    if body:
        params["body"] = body
    return f"mailto:{to_addr}?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)


def _row(cell_style: str, right_style: str, label: str, value) -> str:
    return f'<tr><td style="{cell_style}">{html.escape(str(label))}</td><td style="{cell_style}{right_style}">{money(value)}</td></tr>'


def build_html(r, from_addr: str, next_report: dt.date) -> str:
    cell = "padding:6px 12px;border-bottom:1px solid #e5e5e5;text-align:left;"
    header_cell = cell + "font-weight:600;background:#f5f5f5;"
    right = "text-align:right;"
    font = "font-family:-apple-system,Helvetica,Arial,sans-serif;color:#1a1a1a;"
    button = (
        "display:inline-block;margin:0 8px 8px 0;padding:8px 14px;"
        "background:#f5f5f5;border:1px solid #d0d0d0;border-radius:6px;"
        "color:#1a1a1a;text-decoration:none;font-size:13px;"
    )

    summary_rows = "".join([
        _row(cell, right, "Last 24 hours (today, UTC so far)", r["today_cost"]),
        _row(cell, right, f"Last calendar month ({r['last_month_start'].strftime('%Y-%m')})", r["last_month_cost"]),
        _row(
            cell, right,
            f"Last 3 calendar months ({r['three_months_start'].strftime('%Y-%m')} "
            f"through {r['last_month_start'].strftime('%Y-%m')})",
            r["three_months_cost"],
        ),
    ])

    daily_rows = "".join(
        _row(cell, right, period, cost) for period, cost in r["daily"]
    ) or f'<tr><td style="{cell}" colspan="2">No usage recorded in this window.</td></tr>'

    skip_tomorrow = _mailto(from_addr, f"{CMD_TAG}: SKIP-TOMORROW")
    skip_week = _mailto(from_addr, f"{CMD_TAG}: SKIP-7-DAYS")
    set_date = _mailto(
        from_addr, f"{CMD_TAG}: NEXT-ON YYYY-MM-DD",
        body="Edit the date in the subject above to YYYY-MM-DD format (e.g. 2026-10-15), then send.",
    )

    return f"""\
<html>
  <body style="{font}max-width:600px;margin:0 auto;padding:16px;">
    <h2 style="margin:0 0 4px;">Claude Code token usage</h2>
    <p style="margin:0 0 16px;color:#666;font-size:13px;">
      Generated {r['generated_at'].strftime('%Y-%m-%d %H:%M UTC')} &middot; source: local session logs via ccusage
    </p>

    <table style="width:100%;border-collapse:collapse;margin-bottom:24px;">
      <tr><th style="{header_cell}">Window</th><th style="{header_cell}{right}">Cost</th></tr>
      {summary_rows}
    </table>

    <h3 style="margin:0 0 8px;font-size:14px;">Daily, last {len(r['daily'])} days</h3>
    <table style="width:100%;border-collapse:collapse;margin-bottom:24px;">
      <tr><th style="{header_cell}">Date</th><th style="{header_cell}{right}">Cost</th></tr>
      {daily_rows}
    </table>

    <h3 style="margin:0 0 8px;font-size:14px;">Manage this report</h3>
    <p style="margin:0 0 12px;color:#666;font-size:12px;">
      Next report: {next_report.isoformat()}. Reply with one of these (just send, no editing
      needed for the first two) to change that:
    </p>
    <a href="{skip_tomorrow}" style="{button}">Skip tomorrow's report</a>
    <a href="{skip_week}" style="{button}">Skip the next 7 days</a>
    <a href="{set_date}" style="{button}">Set date of next report&hellip;</a>
  </body>
</html>
"""


def build_text(r, next_report: dt.date) -> str:
    lines = [
        "Claude Code token usage",
        f"Generated {r['generated_at'].strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"Last 24 hours: {money(r['today_cost'])}",
        f"Last calendar month ({r['last_month_start'].strftime('%Y-%m')}): {money(r['last_month_cost'])}",
        f"Last 3 calendar months ({r['three_months_start'].strftime('%Y-%m')} "
        f"through {r['last_month_start'].strftime('%Y-%m')}): {money(r['three_months_cost'])}",
        f"\nDaily, last {len(r['daily'])} days:",
    ]
    for period, cost in r["daily"]:
        lines.append(f"  {period}: {money(cost)}")
    lines.append(f"\nNext report: {next_report.isoformat()}")
    lines.append(f"To change that, reply with subject '{CMD_TAG}: SKIP-TOMORROW', "
                 f"'{CMD_TAG}: SKIP-7-DAYS', or '{CMD_TAG}: NEXT-ON YYYY-MM-DD'.")
    return "\n".join(lines)


def send_email(subject: str, html_body: str, text_body: str, from_addr: str, app_password: str, to_addr: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(from_addr, app_password)
        server.sendmail(from_addr, [to_addr], msg.as_string())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--daily-days",
        type=int,
        default=DEFAULT_DAILY_DAYS,
        help=f"how many trailing days to show in the daily table (default: {DEFAULT_DAILY_DAYS})",
    )
    args = parser.parse_args()

    from_addr, app_password, to_addr = get_credentials()
    today = dt.datetime.now(dt.timezone.utc).date()

    state = apply_inbox_commands(from_addr, app_password, today, load_state())
    save_state(state)

    skip_until = parse_skip_until(state)
    if skip_until and today <= skip_until:
        print(f"Skipped (per reply command): next report on {skip_until + dt.timedelta(days=1)}")
        return

    r = compute_report(args.daily_days)
    subject = build_subject(r)
    next_report = today + dt.timedelta(days=1)
    send_email(subject, build_html(r, from_addr, next_report), build_text(r, next_report), from_addr, app_password, to_addr)
    print(f"Sent to {to_addr}: {subject}")


if __name__ == "__main__":
    main()
