from __future__ import annotations

import os
import time
from datetime import datetime, time as clock_time
from pathlib import Path
from textwrap import dedent

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from app.excel_report import generate_excel_report
from app.mailer import send_report
from app.pdf_report import generate_pdf_report


ROOT = Path(__file__).resolve().parent
CSS_PATH = ROOT / "assets" / "styles.css"


st.set_page_config(page_title="Report Generator", page_icon="📊", layout="centered")
load_dotenv(ROOT / ".env")

if CSS_PATH.exists():
    css = CSS_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_html(html: str) -> None:
    """Render pure HTML without passing it through Markdown code-block parsing."""
    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)


# Premium decorative shell: visual-only layers that do not affect app state or backend calls.
st.markdown(
    dedent("""
    <div class="ambient-shell" aria-hidden="true">
      <div class="aurora aurora-one"></div>
      <div class="aurora aurora-two"></div>
      <div class="aurora aurora-three"></div>
      <div class="grid-sheen"></div>
      <div class="scanline"></div>
    </div>
    <div class="scroll-progress" aria-hidden="true"></div>
    """),
    unsafe_allow_html=True,
)

# SaaS-style top bar. It is informational only, so the 3-step workflow remains unchanged.
st.markdown(
    dedent("""
    <nav class="premium-topbar" aria-label="Application status">
      <div class="brand-lockup">
        <span class="brand-mark">RG</span>
        <span class="brand-copy">
          <strong>Report Generator</strong>
          <small>Automated reporting console</small>
        </span>
      </div>
      <div class="topbar-chips">
        <span class="system-chip live">Live pipeline</span>
        <span class="system-chip">PDF</span>
        <span class="system-chip">Excel</span>
        <span class="system-chip">Email</span>
      </div>
    </nav>
    """),
    unsafe_allow_html=True,
)

for key, default in [
    ("step", 1),
    ("uploaded_df", None),
    ("uploaded_name", ""),
    ("report_config", {}),
    ("pdf_path", None),
    ("xl_path", None),
    ("send_result", None),
    ("pipeline_error", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


def reset_app() -> None:
    for key, value in {
        "step": 1,
        "uploaded_df": None,
        "uploaded_name": "",
        "report_config": {},
        "pdf_path": None,
        "xl_path": None,
        "send_result": None,
        "pipeline_error": None,
    }.items():
        st.session_state[key] = value
    st.rerun()


def rerun_to_step(step: int) -> None:
    st.session_state.step = step
    if step == 3:
        st.session_state.pdf_path = None
        st.session_state.xl_path = None
        st.session_state.send_result = None
        st.session_state.pipeline_error = None
    st.rerun()


def show_step_indicator() -> None:
    step = st.session_state.step
    dot = lambda n: "active" if step >= n else ""
    line = lambda n: "active" if step > n else ""
    st.markdown(
        dedent(f"""
        <div class="step-indicator">
          <div class="step-dot {dot(1)}">1</div>
          <div class="step-line {line(1)}"></div>
          <div class="step-dot {dot(2)}">2</div>
          <div class="step-line {line(2)}"></div>
          <div class="step-dot {dot(3)}">3</div>
        </div>
        <div class="step-labels">
          <span class="{dot(1)}">Upload</span>
          <span class="{dot(2)}">Configure</span>
          <span class="{dot(3)}">Generate</span>
        </div>
        <div class="step-glow step-{step}" aria-hidden="true"></div>
        """),
        unsafe_allow_html=True,
    )


def read_uploaded_file(uploaded_file) -> pd.DataFrame:
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(uploaded_file)
    if suffix in (".xlsx", ".xls"):
        return pd.read_excel(uploaded_file)
    raise ValueError("Unsupported file type. Please upload CSV, XLSX, or XLS.")


def report_icon() -> str:
    return """
<div class="hero-icon">
  <svg viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <circle class="ring" cx="60" cy="60" r="48" stroke="#10b981" stroke-width="3" stroke-dasharray="18 12" opacity="0.7"/>
    <rect x="34" y="28" width="52" height="66" rx="10" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.28)" stroke-width="2"/>
    <path d="M46 48H75" stroke="#fff" stroke-width="5" stroke-linecap="round"/>
    <path d="M46 62H66" stroke="rgba(255,255,255,0.62)" stroke-width="5" stroke-linecap="round"/>
    <path d="M46 78L56 68L65 75L78 58" stroke="#f59e0b" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="79" cy="58" r="5" fill="#10b981"/>
  </svg>
</div>
""".strip()


def stage(status_slot, progress_bar, message: str, value: int) -> None:
    status_slot.markdown(f'<div class="stage-pill">⏳ {message}</div>', unsafe_allow_html=True)
    progress_bar.progress(value)
    time.sleep(0.8)


def run_generation_pipeline(status_slot, progress_bar) -> None:
    try:
        report_config = st.session_state.report_config
        fmt_map = {
            "PDF only": "pdf",
            "Excel only": "excel",
            "Both (PDF + Excel)": "both",
        }
        fmt = fmt_map[report_config["format"]]

        stage(status_slot, progress_bar, "📂 Reading your data...", 0)
        df = st.session_state.uploaded_df.copy()
        selected_columns = report_config.get("columns") or list(df.columns)
        df = df[selected_columns]
        progress_bar.progress(25)
        time.sleep(0.8)

        stage(status_slot, progress_bar, "📊 Generating your report...", 60)
        if fmt in ("pdf", "both"):
            st.session_state.pdf_path = generate_pdf_report(
                df,
                title=report_config["title"],
                company_name=report_config["company"],
            )

        if fmt in ("excel", "both"):
            st.session_state.xl_path = generate_excel_report(
                df,
                title=report_config["title"],
                company_name=report_config["company"],
            )

        stage(status_slot, progress_bar, "📧 Sending email...", 90)
        os.environ["SENDER_EMAIL"] = report_config["sender_email"]
        os.environ["APP_PASSWORD"] = report_config["app_password"]

        attachments = [
            p
            for p in [st.session_state.pdf_path, st.session_state.xl_path]
            if p is not None
        ]

        st.session_state.send_result = send_report(
            recipients=report_config["recipients"],
            subject=report_config["subject"].replace(
                "{date}", datetime.now().strftime("%d %b %Y")
            ),
            body=f"Please find your {report_config['title']} attached.",
            attachments=attachments,
        )

        if not st.session_state.send_result.get("success"):
            raise RuntimeError(st.session_state.send_result.get("error", "Email failed."))

        stage(status_slot, progress_bar, "✅ Done!", 100)
        st.session_state.pipeline_error = None
    except Exception as exc:
        st.session_state.pipeline_error = str(exc)


def show_step_1() -> None:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        # Render hero as pure HTML, not Markdown, so Streamlit cannot display it as a code block.
        render_html(f"""
<div class="hero-shell">
  {report_icon()}
  <h1 class="hero-title">Report Generator</h1>
  <p class="hero-subtitle">Upload your data. Configure your report. Send it automatically.</p>
  <div class="hero-equalizer" aria-hidden="true">
    <span></span><span></span><span></span><span></span><span></span>
  </div>
</div>
""".strip())
        uploaded_file = st.file_uploader(
            "",
            type=["csv", "xlsx", "xls"],
            label_visibility="collapsed",
        )

    if uploaded_file is not None:
        try:
            df = read_uploaded_file(uploaded_file)
            df.columns = [str(col).strip() for col in df.columns]
            df = df.dropna(how="all")
            st.session_state.uploaded_df = df
            st.session_state.uploaded_name = uploaded_file.name
            st.markdown('<div class="preview-title">Data Preview</div>', unsafe_allow_html=True)
            st.dataframe(df.head(50), use_container_width=True)

            numeric_cols = len(df.select_dtypes(include="number").columns)
            stat_cols = st.columns(3)
            stats = [
                ("📊", f"{len(df):,}", "Rows"),
                ("📋", f"{len(df.columns):,}", "Columns"),
                ("🔢", f"{numeric_cols:,}", "Numeric cols"),
            ]
            for target, (icon, value, label) in zip(stat_cols, stats):
                target.markdown(
                    dedent(f"""
                    <div class="stat-pill">
                      <div class="stat-value">{icon} {value}</div>
                      <div class="stat-label">{label}</div>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )

            st.write("")
            if st.button("Next: Configure Report →", type="primary", use_container_width=True):
                rerun_to_step(2)
        except Exception as exc:
            st.error(f"Could not read this file: {exc}")


def show_step_2() -> None:
    if st.session_state.uploaded_df is None:
        rerun_to_step(1)

    df = st.session_state.uploaded_df
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<div class="section-title reveal-left">📄 Report Settings</div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        title = st.text_input("Report title", value=st.session_state.report_config.get("title", "Monthly Report"))
        company = st.text_input("Company name", value=st.session_state.report_config.get("company", "My Company"))
        report_format = st.radio(
            "Report format",
            options=["PDF only", "Excel only", "Both (PDF + Excel)"],
            index=["PDF only", "Excel only", "Both (PDF + Excel)"].index(
                st.session_state.report_config.get("format", "Both (PDF + Excel)")
            ),
            horizontal=True,
        )
        chart_type = st.selectbox(
            "Chart type",
            options=["Bar Chart", "Line Chart", "Pie Chart"],
            index=["Bar Chart", "Line Chart", "Pie Chart"].index(
                st.session_state.report_config.get("chart_type", "Bar Chart")
            ),
        )
        columns = st.multiselect(
            "Columns to include",
            options=list(df.columns),
            default=st.session_state.report_config.get("columns", list(df.columns)),
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-title reveal-right">📧 Email & Schedule</div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        sender_email = st.text_input(
            "Sender Gmail",
            value=st.session_state.report_config.get("sender_email", os.getenv("SENDER_EMAIL", "")),
        )
        app_password = st.text_input(
            "Gmail App Password",
            value=st.session_state.report_config.get("app_password", os.getenv("APP_PASSWORD", "")),
            type="password",
        )
        recipients_text = st.text_area(
            "Recipients",
            value=", ".join(st.session_state.report_config.get("recipients", [])),
            placeholder="email1@gmail.com, email2@gmail.com",
            help="Separate multiple emails with commas",
        )
        subject = st.text_input(
            "Email subject",
            value=st.session_state.report_config.get("subject", "Your Report — {date}"),
        )
        schedule = st.radio(
            "Schedule",
            options=["Send Now", "Daily", "Weekly", "Monthly"],
            index=["Send Now", "Daily", "Weekly", "Monthly"].index(
                st.session_state.report_config.get("schedule", "Send Now")
            ),
            horizontal=True,
        )
        send_at = None
        if schedule in ("Daily", "Weekly", "Monthly"):
            send_at = st.time_input(
                "Send at",
                value=st.session_state.report_config.get("send_at", clock_time(8, 0)),
            )
            st.info("Scheduler not started from UI. Run: python -m app.scheduler")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    nav_left, nav_right = st.columns(2)
    with nav_left:
        if st.button("← Back", use_container_width=True):
            rerun_to_step(1)
    with nav_right:
        recipients = [email.strip() for email in recipients_text.split(",") if email.strip()]
        if st.button("Preview & Generate →", type="primary", use_container_width=True):
            st.session_state.report_config = {
                "title": title,
                "company": company,
                "format": report_format,
                "chart_type": chart_type,
                "columns": columns,
                "sender_email": sender_email,
                "app_password": app_password,
                "recipients": recipients,
                "subject": subject,
                "schedule": schedule,
                "send_at": send_at,
            }
            rerun_to_step(3)


def show_downloads() -> None:
    config = st.session_state.report_config
    generated_at = datetime.now().strftime("%d %b %Y at %H:%M")
    st.markdown('<div class="success-burst">✅</div>', unsafe_allow_html=True)
    st.markdown('<div class="success-title">Report Generated!</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    pdf_path = st.session_state.pdf_path
    xl_path = st.session_state.xl_path

    if pdf_path:
        st.markdown('<div class="result-row"><strong>📄 PDF Report</strong></div>', unsafe_allow_html=True)
        with open(pdf_path, "rb") as f:
            st.download_button(
                "Download PDF",
                f,
                file_name="report.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )

    if xl_path:
        st.markdown('<div class="result-row"><strong>📊 Excel Report</strong></div>', unsafe_allow_html=True)
        with open(xl_path, "rb") as f:
            st.download_button(
                "Download Excel",
                f,
                file_name="report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True,
            )

    st.markdown(
        dedent(f"""
        <p class="muted">📧 Sent to: {", ".join(config.get("recipients", []))}</p>
        <p class="muted">Generated on {generated_at}</p>
        """),
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    if st.button("Generate Another Report", use_container_width=True):
        reset_app()


def show_step_3() -> None:
    if st.session_state.uploaded_df is None or not st.session_state.report_config:
        rerun_to_step(1)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        if (
            st.session_state.send_result is None
            and st.session_state.pipeline_error is None
            and st.session_state.pdf_path is None
            and st.session_state.xl_path is None
        ):
            status_slot = st.empty()
            progress_bar = st.progress(0)
            st.markdown(
                dedent("""
                <div class="loading-deck" aria-hidden="true">
                  <div class="skeleton-card wide"></div>
                  <div class="skeleton-grid">
                    <span></span><span></span><span></span>
                  </div>
                </div>
                """),
                unsafe_allow_html=True,
            )
            run_generation_pipeline(status_slot, progress_bar)
            status_slot.empty()

        if st.session_state.pipeline_error:
            st.markdown(
                dedent(f"""
                <div class="error-card">
                  <strong>Report generation failed</strong><br>
                  {st.session_state.pipeline_error}
                </div>
                """),
                unsafe_allow_html=True,
            )
            st.write("")
            if st.button("Try Again", type="primary", use_container_width=True):
                rerun_to_step(2)
        else:
            show_downloads()


show_step_indicator()

if st.session_state.step == 1:
    show_step_1()
elif st.session_state.step == 2:
    show_step_2()
else:
    show_step_3()
