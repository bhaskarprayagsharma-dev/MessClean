from modules.tool_registry import get_tools
from modules.metadata_manager import initialize_metadata

import tools.clean_quantity_tool
import tools.clean_currency_tool
import tools.clean_percentage_tool
import tools.clean_date_format_tool
import tools.remove_duplicates_tool
import tools.remove_empty_columns
import tools.detect_summary_rows_tool
import tools.semantic_column_mapper


def run_detect_pipeline(df):
    """
    Run all tools in detect mode. Returns (metadata, list of proposed changes).
    Does not modify df. Proposed changes have: change_id, tool, scope, target,
    target_display, before_sample, after_sample.
    """
    metadata = initialize_metadata()
    all_proposed = []

    tools = get_tools()

    for name, tool in tools:
        if hasattr(tool, "detect"):
            proposed = tool.detect(df.copy(), metadata)
            all_proposed.extend(proposed)
        else:
            # Tools without detect (e.g. semantic_column_mapper): run to populate metadata
            df, metadata, _ = tool(df, metadata)

    return metadata, all_proposed


def run_apply_pipeline(df, metadata, approved_change_ids, reports=None):
    """
    Run all tools in apply mode, applying only approved changes.
    approved_change_ids: set or list of change_ids user approved.
    Returns (df, metadata, reports).
    """
    if reports is None:
        reports = []

    approved = set(approved_change_ids) if approved_change_ids else set()
    tools = get_tools()

    for name, tool in tools:
        if hasattr(tool, "apply"):
            df, metadata, report = tool.apply(df, metadata, approved)
        else:
            df, metadata, report = tool(df, metadata)

        reports.append({"tool": name, "report": report})

    return df, metadata, reports


def run_pipeline(df, approved_change_ids=None):
    """
    Full pipeline. If approved_change_ids is None, runs legacy mode (all tools apply
    everything, no preview). Otherwise runs apply-only with approved changes.
    """
    metadata = initialize_metadata()
    reports = []

    if approved_change_ids is None:
        # Legacy: run each tool with no approval filter (tools apply all)
        approved = None  # signals "apply all" to tools that support it
    else:
        approved = set(approved_change_ids)

    tools = get_tools()

    for name, tool in tools:
        if hasattr(tool, "apply") and approved is not None:
            df, metadata, report = tool.apply(df, metadata, approved)
        elif hasattr(tool, "apply") and approved is None:
            # Apply-all: get all proposed and pass them as approved
            proposed = tool.detect(df.copy(), metadata) if hasattr(tool, "detect") else []
            all_ids = [p["change_id"] for p in proposed]
            df, metadata, report = tool.apply(df, metadata, set(all_ids))
        else:
            df, metadata, report = tool(df, metadata)

        reports.append({"tool": name, "report": report})

    return df, metadata, reports
