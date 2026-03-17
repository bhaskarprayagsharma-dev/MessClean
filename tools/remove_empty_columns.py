from modules.tool_registry import register_tool
from modules.proposed_change import make_change_id


def _is_empty_column(series):
    """True if column is all NaN or all blank/whitespace."""
    if series.isna().all():
        return True
    stripped = series.astype(str).str.strip()
    return (stripped == "").all()


def detect(df, metadata):
    empty_columns = [c for c in df.columns if _is_empty_column(df[c])]
    proposed = []
    for col in empty_columns:
        proposed.append({
            "change_id": make_change_id("remove_empty_columns_tool", col),
            "tool": "remove_empty_columns_tool",
            "scope": "column",
            "target": col,
            "target_display": f"Column: {col} (empty)",
            "before_sample": ["(all empty)"] * 3,
            "after_sample": ["(would be removed)"],
        })
    return proposed


def apply(df, metadata, approved_change_ids):
    empty_columns = [c for c in df.columns if _is_empty_column(df[c])]
    to_remove = [c for c in empty_columns if make_change_id("remove_empty_columns_tool", c) in approved_change_ids]
    df = df.drop(columns=to_remove)
    metadata["operations"].append(f"Removed {len(to_remove)} empty columns")
    report = {"empty_columns_removed": to_remove}
    return df, metadata, report


from types import SimpleNamespace
register_tool("remove_empty_columns_tool", SimpleNamespace(detect=detect, apply=apply))
