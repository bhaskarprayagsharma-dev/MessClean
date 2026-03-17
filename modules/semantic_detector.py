import re


def detect_semantic_type(series):
    sample = series.dropna().astype(str).head(20)

    qty_pattern = re.compile(r"\d+\s?(kg|pcs|g|btl|ltr)", re.I)
    currency_pattern = re.compile(r"[₹$€]\s?\d+")
    percent_pattern = re.compile(r"\d+%")

    for val in sample:
        if qty_pattern.search(val):
            return "quantity"
        if currency_pattern.search(val):
            return "currency"
        if percent_pattern.search(val):
            return "percentage"

    return "unknown"
