import pandas as pd
from datetime import datetime
from io import BytesIO

# App / website details embedded in the report
APP_NAME = "Excel Data Cleaner"
APP_URL = "https://excel-data-cleaner.example.com"  # Update with your actual URL
APP_DESCRIPTION = "Fix messy Excel files in seconds with automated cleaning."

# Human-friendly names for tools in the report
TOOL_DISPLAY_NAMES = {
    "semantic_column_mapper": "Column type analysis",
    "clean_quantity_tool": "Quantity cleaning",
    "clean_currency_tool": "Currency cleaning",
    "clean_percentage_tool": "Percentage cleaning",
    "clean_date_format_tool": "Date formatting",
    "remove_empty_columns_tool": "Remove empty columns",
    "detect_summary_rows_tool": "Summary row removal",
    "remove_duplicates_tool": "Duplicate row removal",
}


def build_cleaning_report(metadata, reports):
    """Build a report DataFrame with operations and tool details."""
    report_rows = []

    # operations summary
    for op in metadata.get("operations", []):
        report_rows.append({
            "Step": "Operation",
            "Details": op
        })

    # tool reports
    for tool in reports:
        tool_name = tool.get("tool")
        report_rows.append({
            "Step": tool_name,
            "Details": str(tool.get("report"))
        })

    return pd.DataFrame(report_rows)


def build_report_sheet_content(metadata, reports, cleaned_df):
    """Build full report content. Column analysis only includes columns present in output."""
    rows = []
    output_columns = set(cleaned_df.columns) if cleaned_df is not None else set()
    cleaned_rows = len(cleaned_df) if cleaned_df is not None else 0
    cleaned_cols = len(cleaned_df.columns) if cleaned_df is not None else 0

    # --- App / website details ---
    rows.append(["Report: Excel Data Cleaner"])
    rows.append([])
    rows.append(["Service", APP_NAME])
    rows.append(["Website", APP_URL])
    rows.append(["Description", APP_DESCRIPTION])
    rows.append(["Processed", datetime.now().strftime("%Y-%m-%d %H:%M")])
    rows.append([])

    # --- Summary ---
    rows.append(["Summary"])
    rows.append(["Output columns", cleaned_cols])
    rows.append(["Output rows", cleaned_rows])
    rows.append(["Operations performed", len(metadata.get("operations", []))])
    rows.append([])

    # --- Column metadata (only columns still in output) ---
    if metadata.get("columns") and output_columns:
        rows.append(["Column analysis (output columns only)"])
        for col, info in metadata["columns"].items():
            if col in output_columns:
                rows.append([f"  {col}", str(info)])
        rows.append([])

    # --- Operations log ---
    rows.append(["Operations log"])
    for op in metadata.get("operations", []):
        rows.append(["-", op])
    rows.append([])

    # --- Tool reports (human-friendly names) ---
    rows.append(["Tool reports"])
    for tool in reports:
        raw_name = tool.get("tool", "")
        display_name = TOOL_DISPLAY_NAMES.get(raw_name, raw_name)
        rows.append([display_name, str(tool.get("report", ""))])

    return rows


def build_excel_with_report(cleaned_df, metadata, reports, file_name="cleaned_data.xlsx"):
    """
    Build an Excel file with two sheets:
    - 'Cleaned Data': the cleaned DataFrame
    - 'Report': summary, app details, metadata, and operations log
    Returns bytes for download.
    """
    buffer = BytesIO()

    report_rows = build_report_sheet_content(metadata, reports, cleaned_df)
    report_df = pd.DataFrame(report_rows)

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        cleaned_df.to_excel(writer, sheet_name="Cleaned Data", index=False)
        report_df.to_excel(writer, sheet_name="Report", index=False, header=False)

    buffer.seek(0)
    return buffer.getvalue()
