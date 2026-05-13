"""
Sprint 1 verification script.
Run with: python test_sprint1.py
"""

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))

from app.excel_report import generate_excel_report
from app.pdf_report import generate_pdf_report
from app.reader import get_summary_stats, load_data


def main() -> None:
    """Run the full Sprint 1 backend verification flow."""
    os.makedirs("data", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    print("Creating sample datasets...")
    sales_data = {
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "Product": ["Product A"] * 6 + ["Product B"] * 6,
        "Units_Sold": [120, 135, 110, 145, 160, 130, 90, 105, 95, 115, 125, 140],
        "Revenue": [45000, 51000, 41000, 55000, 61000, 49000, 34000, 39000, 36000, 43000, 47000, 53000],
        "Expenses": [28000, 31000, 27000, 34000, 38000, 30000, 22000, 25000, 23000, 27000, 29000, 33000],
        "Profit": [17000, 20000, 14000, 21000, 23000, 19000, 12000, 14000, 13000, 16000, 18000, 20000],
    }
    pd.DataFrame(sales_data).to_csv("data/sales_data.csv", index=False)
    print("  ✓ data/sales_data.csv created")

    emp_data = {
        "Employee_ID": [f"EMP{i:03d}" for i in range(1, 11)],
        "Name": [
            "Ravi Sharma",
            "Priya Patel",
            "Amit Shah",
            "Sneha Joshi",
            "Karan Mehta",
            "Pooja Verma",
            "Rahul Gupta",
            "Anita Singh",
            "Vijay Kumar",
            "Neha Desai",
        ],
        "Department": ["Sales", "HR", "Tech", "Sales", "Tech", "HR", "Tech", "Sales", "HR", "Tech"],
        "Attendance_Days": [24, 22, 25, 23, 26, 21, 25, 24, 22, 26],
        "Leave_Days": [2, 4, 1, 3, 0, 5, 1, 2, 4, 0],
        "Performance_Score": [88, 76, 92, 81, 95, 70, 89, 84, 74, 93],
    }
    pd.DataFrame(emp_data).to_excel("data/employee_data.xlsx", index=False)
    print("  ✓ data/employee_data.xlsx created")

    print("\nLoading datasets...")
    df_sales = load_data("data/sales_data.csv")
    df_emp = load_data("data/employee_data.xlsx")
    assert len(df_sales) == 12, "Sales data should have 12 rows"
    assert len(df_emp) == 10, "Employee data should have 10 rows"
    print(f"  ✓ Sales data: {len(df_sales)} rows, {len(df_sales.columns)} columns")
    print(f"  ✓ Employee data: {len(df_emp)} rows, {len(df_emp.columns)} columns")

    print("\nGenerating summary stats...")
    stats = get_summary_stats(df_sales)
    assert stats["row_count"] == 12
    assert "Revenue" in stats["numeric_summary"]
    print(f"  ✓ Stats generated: {stats['row_count']} rows, {len(stats['numeric_summary'])} numeric columns")

    print("\nGenerating PDF reports...")
    pdf1 = generate_pdf_report(df_sales, title="Monthly Sales Report", company_name="Demo Company")
    pdf2 = generate_pdf_report(df_emp, title="Employee Attendance Report", company_name="Demo Company")
    assert os.path.exists(pdf1), f"PDF not found: {pdf1}"
    assert os.path.exists(pdf2), f"PDF not found: {pdf2}"
    print(f"  ✓ {pdf1}")
    print(f"  ✓ {pdf2}")

    print("\nGenerating Excel reports...")
    xl1 = generate_excel_report(df_sales, title="Monthly Sales Report", company_name="Demo Company")
    xl2 = generate_excel_report(df_emp, title="Employee Attendance Report", company_name="Demo Company")
    assert os.path.exists(xl1), f"Excel not found: {xl1}"
    assert os.path.exists(xl2), f"Excel not found: {xl2}"
    print(f"  ✓ {xl1}")
    print(f"  ✓ {xl2}")

    print("\n" + "=" * 45)
    print("SPRINT 1 COMPLETE ✓")
    print("=" * 45)
    print(f"outputs/ contains {len(os.listdir('outputs'))} files")
    print("Open the PDF and Excel files to verify formatting.")


if __name__ == "__main__":
    main()
