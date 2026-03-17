import pandas as pd
from modules.tool_registry import register_tool
from modules.proposed_change import make_change_id

SAMPLE_SIZE = 8


def detect(df, metadata):
    proposed = []
    for col in df.columns:
        try:
            ser = df[col].reset_index(drop=True)
            converted = pd.to_datetime(ser, errors="coerce")
            if converted.notnull().sum() > len(df) * 0.6:
                n = min(SAMPLE_SIZE, len(ser))
                before = ser.astype(str).head(n).tolist()
                after = [
                    (str(converted.iloc[i])[:19] if pd.notna(converted.iloc[i]) else before[i])
                    for i in range(n)
                ]
                if before != after:
                    proposed.append({
                        "change_id": make_change_id("clean_date_format_tool", col),
                        "tool": "clean_date_format_tool",
                        "scope": "column",
                        "target": col,
                        "target_display": f"Column: {col}",
                        "before_sample": before,
                        "after_sample": after,
                    })
        except Exception:
            pass
    return proposed


def apply(df, metadata, approved_change_ids):
    report = []
    for col in df.columns:
        if make_change_id("clean_date_format_tool", col) in approved_change_ids:
            try:
                converted = pd.to_datetime(df[col], errors="coerce")
                if converted.notnull().sum() > len(df) * 0.6:
                    df[col] = converted
                    metadata["operations"].append(f"Date normalized in {col}")
                    report.append(col)
            except Exception:
                pass
    return df, metadata, report


from types import SimpleNamespace
register_tool("clean_date_format_tool", SimpleNamespace(detect=detect, apply=apply))
