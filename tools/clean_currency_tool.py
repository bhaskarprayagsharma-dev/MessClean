import re
from modules.tool_registry import register_tool
from modules.proposed_change import make_change_id

SAMPLE_SIZE = 8


def _parse_currency_value(val):
    """Extract numeric value from currency string, preserving decimals.
    Handles: 1,234.56 (US), 1.234,56 (EU), and simple cases like ₹100 or $1.5
    """
    s = str(val).strip()
    s = re.sub(r"[₹$€£\s]", "", s)
    s = re.sub(r"[^\d.,]", "", s)
    if not s:
        return ""

    last_comma = s.rfind(",")
    last_period = s.rfind(".")
    if last_comma > last_period:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", "")

    return s


def detect(df, metadata):
    """Return proposed changes with before/after preview. Does not modify df."""
    proposed = []

    for col in df.columns:
        sample = df[col].astype(str).head(20)
        if any(re.search(r"[₹$€£]", v) for v in sample):
            before = df[col].astype(str).head(SAMPLE_SIZE).tolist()
            after = [_parse_currency_value(v) for v in before]
            if before != after:  # only propose if there's actual change
                proposed.append({
                    "change_id": make_change_id("clean_currency_tool", col),
                    "tool": "clean_currency_tool",
                    "scope": "column",
                    "target": col,
                    "target_display": f"Column: {col}",
                    "before_sample": before,
                    "after_sample": after,
                })

    return proposed


def apply(df, metadata, approved_change_ids):
    """Apply only approved currency cleanings. Returns (df, metadata, report)."""
    report = []
    for col in df.columns:
        cid = make_change_id("clean_currency_tool", col)
        if cid in approved_change_ids:
            cleaned = [_parse_currency_value(v) for v in df[col].astype(str)]
            df[col] = cleaned
            metadata["operations"].append(f"Currency cleaned in {col}")
            report.append(col)

    return df, metadata, report


from types import SimpleNamespace
register_tool("clean_currency_tool", SimpleNamespace(detect=detect, apply=apply))
