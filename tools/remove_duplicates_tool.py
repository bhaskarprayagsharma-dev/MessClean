from modules.tool_registry import register_tool
from modules.proposed_change import make_change_id


def detect(df, metadata):
    before_rows = len(df)
    df_unique = df.drop_duplicates()
    after_rows = len(df_unique)
    removed = before_rows - after_rows

    proposed = []
    if removed > 0:
        dupes = df[df.duplicated(keep="first")]
        before_sample = dupes.head(5).values.tolist() if len(dupes) > 0 else []
        proposed.append({
            "change_id": make_change_id("remove_duplicates_tool", "duplicates"),
            "tool": "remove_duplicates_tool",
            "scope": "row",
            "target": f"{removed} rows",
            "target_display": f"Remove {removed} duplicate rows",
            "before_sample": before_sample[:5],
            "after_sample": [f"(duplicates of above would be removed)"],
        })
    return proposed


def apply(df, metadata, approved_change_ids):
    change_id = make_change_id("remove_duplicates_tool", "duplicates")
    if change_id not in approved_change_ids:
        return df, metadata, {"duplicates_removed": 0}

    before_rows = len(df)
    df = df.drop_duplicates()
    after_rows = len(df)
    removed = before_rows - after_rows

    metadata["operations"].append(f"Removed {removed} duplicate rows")
    report = {"duplicates_removed": removed}
    return df, metadata, report


from types import SimpleNamespace
register_tool("remove_duplicates_tool", SimpleNamespace(detect=detect, apply=apply))
