import re
from modules.tool_registry import register_tool
from modules.proposed_change import make_change_id

SAMPLE_SIZE = 8


def _parse_percentage(val):
    s = str(val).strip().replace("%", "")
    s = re.sub(r"[^\d.]", "", s)
    return s


def detect(df, metadata):
    proposed = []
    for col in df.columns:
        sample = df[col].astype(str).head(20)
        if any("%" in v for v in sample):
            before = df[col].astype(str).head(SAMPLE_SIZE).tolist()
            after = [_parse_percentage(v) for v in before]
            if before != after:
                proposed.append({
                    "change_id": make_change_id("clean_percentage_tool", col),
                    "tool": "clean_percentage_tool",
                    "scope": "column",
                    "target": col,
                    "target_display": f"Column: {col}",
                    "before_sample": before,
                    "after_sample": after,
                })
    return proposed


def apply(df, metadata, approved_change_ids):
    report = []
    for col in df.columns:
        if make_change_id("clean_percentage_tool", col) in approved_change_ids:
            df[col] = [_parse_percentage(v) for v in df[col].astype(str)]
            metadata["operations"].append(f"Percentage cleaned in {col}")
            report.append(col)
    return df, metadata, report


from types import SimpleNamespace
register_tool("clean_percentage_tool", SimpleNamespace(detect=detect, apply=apply))
