from modules.tool_registry import register_tool
from modules.proposed_change import make_change_id


def detect(df, metadata):
    keywords = ["total", "subtotal", "grand total"]
    rows_to_remove = []
    for i, row in df.iterrows():
        for cell in row.astype(str):
            if any(k in cell.lower() for k in keywords):
                rows_to_remove.append(i)
                break

    proposed = []
    change_id = make_change_id("detect_summary_rows_tool", "rows")
    if rows_to_remove:
        before_sample = [df.loc[idx].tolist()[:5] for idx in rows_to_remove[:5]]
        proposed.append({
            "change_id": change_id,
            "tool": "detect_summary_rows_tool",
            "scope": "row",
            "target": rows_to_remove,
            "target_display": f"{len(rows_to_remove)} summary rows (indices: {rows_to_remove[:10]}{'...' if len(rows_to_remove) > 10 else ''})",
            "before_sample": before_sample,
            "after_sample": ["(would be removed)"],
        })
    return proposed


def apply(df, metadata, approved_change_ids):
    change_id = make_change_id("detect_summary_rows_tool", "rows")
    if change_id not in approved_change_ids:
        return df, metadata, []

    keywords = ["total", "subtotal", "grand total"]
    rows_to_remove = []
    for i, row in df.iterrows():
        for cell in row.astype(str):
            if any(k in cell.lower() for k in keywords):
                rows_to_remove.append(i)
                break

    df = df.drop(rows_to_remove)
    metadata["operations"].append(f"Removed {len(rows_to_remove)} summary rows")
    return df, metadata, rows_to_remove


from types import SimpleNamespace
register_tool("detect_summary_rows_tool", SimpleNamespace(detect=detect, apply=apply))
