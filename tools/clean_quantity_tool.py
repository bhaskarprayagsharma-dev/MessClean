import re
from modules.tool_registry import register_tool
from modules.proposed_change import make_change_id

SAMPLE_SIZE = 8


def _parse_quantity(val):
    v = str(val)
    match = re.match(r"(\d+)\s?([a-zA-Z]+)?", v)
    if match:
        return match.group(1), match.group(2) if match.group(2) else None
    return v, None


def detect(df, metadata):
    proposed = []
    for col in df.columns:
        sample = df[col].astype(str).head(20)
        if any(re.search(r"\d+\s?(kg|pcs|g|btl|ltr)", v, re.I) for v in sample):
            before = df[col].astype(str).head(SAMPLE_SIZE).tolist()
            after = [_parse_quantity(v)[0] for v in before]
            after_units = [_parse_quantity(v)[1] for v in before]
            if before != after:
                proposed.append({
                    "change_id": make_change_id("clean_quantity_tool", col),
                    "tool": "clean_quantity_tool",
                    "scope": "column",
                    "target": col,
                    "target_display": f"Column: {col} (split number + unit)",
                    "before_sample": before,
                    "after_sample": [f"{n} | unit: {u}" for n, u in zip(after, after_units)],
                })
    return proposed


def apply(df, metadata, approved_change_ids):
    report = []
    cols_to_process = [
        c for c in df.columns
        if make_change_id("clean_quantity_tool", c) in approved_change_ids
    ]
    for col in cols_to_process:
        numbers, units = [], []
        for v in df[col].astype(str):
            n, u = _parse_quantity(v)
            numbers.append(n)
            units.append(u)
        df[col] = numbers
        loc = df.columns.get_loc(col) + 1
        df.insert(loc, col + "_unit", units)
        metadata["operations"].append(f"Quantity cleaned in column {col}")
        report.append(col)
    return df, metadata, report


from types import SimpleNamespace
register_tool("clean_quantity_tool", SimpleNamespace(detect=detect, apply=apply))
