"""
Sprint 2 verification — sends a real test email.
Before running:
  1. Fill in .env: SENDER_EMAIL and APP_PASSWORD
  2. Make sure you have a Gmail App Password set up
     (Google Account → Security → 2FA → App Passwords)
  3. Edit TEST_RECIPIENT below to your own email
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.excel_report import generate_excel_report
from app.mailer import send_report
from app.pdf_report import generate_pdf_report
from app.reader import load_data
from app.scheduler import load_config, run_pipeline

TEST_RECIPIENT = "your_email@gmail.com"  # CHANGE THIS

os.makedirs("outputs", exist_ok=True)

print("=" * 45)
print("SPRINT 2 TEST — Report Generator + Email")
print("=" * 45)

# Test 1: Load config
print("\n[1] Loading config.json...")
config = load_config()
print(f"    ✓ Config loaded: {config['report_title']}")
print(f"    ✓ Schedule: {config['schedule']['type']} at {config['schedule'].get('time', 'now')}")

# Test 2: Generate reports manually
print("\n[2] Generating reports...")
df = load_data(config["data_file"])
pdf_path = generate_pdf_report(
    df,
    title=config["report_title"],
    company_name=config["company_name"],
)
xl_path = generate_excel_report(
    df,
    title=config["report_title"],
    company_name=config["company_name"],
)
print(f"    ✓ PDF:   {pdf_path}")
print(f"    ✓ Excel: {xl_path}")

# Test 3: Send real email
print(f"\n[3] Sending test email to {TEST_RECIPIENT}...")
print("    (check your inbox in ~30 seconds)")
result = send_report(
    recipients=[TEST_RECIPIENT],
    subject="[TEST] Report Generator — Sprint 2 Verification",
    body=(
        "This is a test email from your Report Generator project.\n\n"
        "Both PDF and Excel reports are attached.\n\n"
        "Sprint 2 is working correctly!"
    ),
    attachments=[pdf_path, xl_path],
)

if result["success"]:
    print(f"    ✓ {result['message']}")
else:
    print(f"    ✗ Email failed: {result['error']}")
    print("    → Check SENDER_EMAIL and APP_PASSWORD in .env")
    print("    → Make sure App Password is enabled on your Google account")
    sys.exit(1)

# Test 4: Test run_pipeline() with "now" schedule
print("\n[4] Testing full pipeline via run_pipeline()...")
config["schedule"]["type"] = "now"
config["email"]["recipients"] = [TEST_RECIPIENT]
pipeline_result = run_pipeline(config)
if pipeline_result["success"]:
    print(f"    ✓ Pipeline complete — {pipeline_result['message']}")
else:
    print(f"    ✗ Pipeline failed: {pipeline_result['error']}")

print("\n" + "=" * 45)
print("SPRINT 2 COMPLETE ✓")
print("=" * 45)
print("Check your inbox — you should have 2 emails:")
print("  · Test email with 2 attachments")
print("  · Pipeline email with 2 attachments")
print("\nTo start the scheduler, run:")
print("  python -m app.scheduler")
