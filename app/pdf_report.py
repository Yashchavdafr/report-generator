"""PDF report generation utilities."""

from __future__ import annotations

import os
import tempfile
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.reader import get_summary_stats


NAVY = colors.HexColor("#1a2744")
LIGHT_ROW = colors.HexColor("#f0f4ff")
MUTED_GREY = colors.HexColor("#6b7280")


def _pick_chart_columns(df: pd.DataFrame) -> tuple[str | None, str | None]:
    numeric_columns = list(df.select_dtypes(include="number").columns)
    if not numeric_columns:
        return None, None
    y_col = str(numeric_columns[0])

    x_col = None
    for col in df.columns:
        if str(col) == y_col:
            continue
        if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_datetime64_any_dtype(df[col]):
            x_col = str(col)
            break
    if x_col is None:
        x_col = str(df.columns[0])

    return x_col, y_col


def _build_summary_table_data(df: pd.DataFrame) -> list[list[str]]:
    stats = get_summary_stats(df)
    rows: list[list[str]] = [
        ["Metric", "Value"],
        ["Total Records", str(stats["row_count"])],
        ["Total Columns", str(stats["col_count"])],
        ["Numeric Columns Count", str(len(stats["numeric_summary"]))],
    ]

    for column, column_stats in stats["numeric_summary"].items():
        rows.append([f"{column} Min", f"{column_stats['min']:,.2f}"])
        rows.append([f"{column} Max", f"{column_stats['max']:,.2f}"])
        rows.append([f"{column} Mean", f"{column_stats['mean']:,.2f}"])
        rows.append([f"{column} Sum", f"{column_stats['sum']:,.2f}"])

    return rows


def generate_pdf_report(
    df: pd.DataFrame,
    title: str = "Data Report",
    company_name: str = "Report Generator",
    output_path: str = None,
) -> str:
    """
    Generate a formatted PDF report from a DataFrame and save it to disk.
    """
    os.makedirs("outputs", exist_ok=True)
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        output_path = os.path.join("outputs", f"report_{timestamp}.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1.2 * cm,
        leftMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    styles = getSampleStyleSheet()
    body = styles["BodyText"]
    body.textColor = MUTED_GREY
    body.fontSize = 9

    title_style = styles["Title"]
    title_style.textColor = NAVY
    title_style.fontSize = 22

    story = [
        Paragraph(company_name, body),
        Spacer(1, 6),
        Paragraph(title, title_style),
        Spacer(1, 6),
        Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"Rows: {len(df)} | Columns: {len(df.columns)}",
            body,
        ),
        Spacer(1, 8),
        HRFlowable(color=colors.HexColor("#d1d5db"), thickness=1),
        Spacer(1, 12),
    ]

    summary_data = _build_summary_table_data(df)
    summary_table = Table(summary_data, colWidths=[8 * cm, 8 * cm], repeatRows=1)
    summary_style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db")),
    ]
    for row_idx in range(1, len(summary_data)):
        bg = LIGHT_ROW if row_idx % 2 else colors.white
        summary_style.append(("BACKGROUND", (0, row_idx), (-1, row_idx), bg))
    summary_table.setStyle(TableStyle(summary_style))

    story.extend([Paragraph("Summary Statistics", styles["Heading3"]), Spacer(1, 6), summary_table, Spacer(1, 14)])

    temp_chart = None
    try:
        x_col, y_col = _pick_chart_columns(df)
        if x_col and y_col:
            chart_df = df[[x_col, y_col]].dropna().head(30)
            if not chart_df.empty:
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.bar(chart_df[x_col].astype(str), chart_df[y_col], color="#1a2744")
                ax.set_title(f"{y_col} by {x_col}", fontsize=10)
                ax.tick_params(axis="x", rotation=30, labelsize=8)
                ax.tick_params(axis="y", labelsize=8)
                plt.tight_layout()

                tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                temp_chart = tmp.name
                tmp.close()
                fig.savefig(temp_chart, dpi=120)
                plt.close(fig)

                story.extend(
                    [
                        Paragraph("Data Chart", styles["Heading3"]),
                        Spacer(1, 6),
                        Image(temp_chart, width=16 * cm, height=8 * cm),
                        Spacer(1, 12),
                    ]
                )
    except Exception:
        # Chart issues should not fail full report generation.
        pass

    table_rows = [list(map(str, df.columns))]
    for row in df.fillna("").astype(str).values.tolist():
        table_rows.append(row)

    available_width = doc.width
    col_width = available_width / max(len(df.columns), 1)
    data_table = Table(table_rows, colWidths=[col_width] * len(df.columns), repeatRows=1)
    data_style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d1d5db")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    for row_idx in range(1, len(table_rows)):
        bg = LIGHT_ROW if row_idx % 2 else colors.white
        data_style.append(("BACKGROUND", (0, row_idx), (-1, row_idx), bg))
    data_table.setStyle(TableStyle(data_style))

    story.extend([Paragraph("Full Data Table", styles["Heading3"]), Spacer(1, 6), data_table, Spacer(1, 14)])
    story.append(
        Paragraph(
            '<para align="center"><font size="8" color="#6b7280">'
            "Generated by Report Generator · Yash Chavda"
            "</font></para>"
        )
    )

    doc.build(story)

    if temp_chart and os.path.exists(temp_chart):
        try:
            os.remove(temp_chart)
        except OSError:
            pass

    return output_path
