"""Report pipeline orchestration and APScheduler integration."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

from app.excel_report import generate_excel_report
from app.mailer import send_report
from app.pdf_report import generate_pdf_report
from app.reader import load_data

load_dotenv()


def load_config(config_path: str = "config.json") -> dict:
    """Load and return the config.json as a dict."""
    with open(config_path, encoding="utf-8") as config_file:
        return json.load(config_file)


def _format_placeholders(text: str, report_title: str) -> str:
    """Replace {date} and {report_title} in email templates."""
    date_str = datetime.now().strftime("%d %b %Y")
    return (
        text.replace("{date}", date_str).replace("{report_title}", report_title)
    )


def _parse_schedule_time(time_value: str) -> tuple[int, int]:
    """Parse 'HH:MM' into hour and minute integers."""
    parts = time_value.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid schedule time '{time_value}', expected HH:MM")
    hour = int(parts[0])
    minute = int(parts[1])
    return hour, minute


def run_pipeline(config: dict) -> dict:
    """
    Execute the full report generation + email pipeline.

    Steps:
    1. Load data from config["data_file"] using load_data()
    2. Generate reports based on config["report_format"]:
       - "pdf"   → generate_pdf_report() only
       - "excel" → generate_excel_report() only
       - "both"  → generate both, collect both file paths
    3. Replace {date} and {report_title} placeholders in
       email subject and body using datetime.now().strftime("%d %b %Y")
    4. Call send_report() with:
       - recipients from config["email"]["recipients"]
       - formatted subject and body
       - attachments = list of generated file paths
    5. Log result:
       - Print: "[TIMESTAMP] Pipeline run — SUCCESS: sent to N recipients"
       - Or:    "[TIMESTAMP] Pipeline run — FAILED: "
    6. Return result dict from send_report()
    """
    os.makedirs("outputs", exist_ok=True)

    report_format = str(config.get("report_format", "both")).lower()
    report_title = config["report_title"]
    company_name = config["company_name"]

    df = load_data(config["data_file"])
    attachments: list[str] = []

    if report_format == "pdf":
        attachments.append(
            generate_pdf_report(df, title=report_title, company_name=company_name)
        )
    elif report_format == "excel":
        attachments.append(
            generate_excel_report(df, title=report_title, company_name=company_name)
        )
    elif report_format == "both":
        attachments.append(
            generate_pdf_report(df, title=report_title, company_name=company_name)
        )
        attachments.append(
            generate_excel_report(df, title=report_title, company_name=company_name)
        )
    else:
        err = f"Invalid report_format: {report_format}"
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] Pipeline run — FAILED: {err}")
        return {"success": False, "error": err}

    email_cfg = config["email"]
    subject = _format_placeholders(email_cfg["subject"], report_title)
    body = _format_placeholders(email_cfg["body"], report_title)
    recipients = email_cfg["recipients"]

    result = send_report(
        recipients=recipients,
        subject=subject,
        body=body,
        attachments=attachments,
    )

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if result.get("success"):
        n = len(recipients)
        print(f"[{ts}] Pipeline run — SUCCESS: sent to {n} recipients")
    else:
        print(f"[{ts}] Pipeline run — FAILED: {result.get('error', '')}")

    return result


def start_scheduler(config_path: str = "config.json") -> None:
    """
    Start the APScheduler based on config schedule settings.

    Logic:
    - Load config
    - If config["schedule"]["type"] == "now":
        run_pipeline(config) immediately, then exit
    - If "daily":
        Parse config["schedule"]["time"] as HH:MM
        Schedule: CronTrigger(hour=HH, minute=MM)
        Print: "Scheduler started — running daily at HH:MM"
        Print: "Press Ctrl+C to stop."
        Start BlockingScheduler
    - If "weekly":
        CronTrigger(day_of_week="mon", hour=HH, minute=MM)
    - If "monthly":
        CronTrigger(day=1, hour=HH, minute=MM)
    - All scheduled modes: run once immediately on startup,
      then continue on schedule
    """
    config = load_config(config_path)
    schedule_type = str(config["schedule"]["type"]).lower()
    time_str = config["schedule"].get("time", "08:00")

    if schedule_type == "now":
        run_pipeline(config)
        return

    hour, minute = _parse_schedule_time(str(time_str))

    scheduler = BlockingScheduler()

    def scheduled_job() -> None:
        cfg = load_config(config_path)
        run_pipeline(cfg)

    if schedule_type == "daily":
        trigger = CronTrigger(hour=hour, minute=minute)
        print(f"Scheduler started — running daily at {time_str}")
    elif schedule_type == "weekly":
        trigger = CronTrigger(day_of_week="mon", hour=hour, minute=minute)
        print(f"Scheduler started — running weekly on Monday at {time_str}")
    elif schedule_type == "monthly":
        trigger = CronTrigger(day=1, hour=hour, minute=minute)
        print(f"Scheduler started — running monthly on day 1 at {time_str}")
    else:
        print(f"Unknown schedule type: {schedule_type}", file=sys.stderr)
        sys.exit(1)

    scheduler.add_job(scheduled_job, trigger=trigger)

    print("Press Ctrl+C to stop.")
    run_pipeline(load_config(config_path))

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\nScheduler stopped.")


if __name__ == "__main__":
    start_scheduler()
