TOOL_REGISTRY = {}

# Explicit pipeline order. Tools run in this sequence.
PIPELINE_ORDER = [
    "semantic_column_mapper",
    "clean_quantity_tool",
    "clean_currency_tool",
    "clean_percentage_tool",
    "clean_date_format_tool",
    "remove_empty_columns_tool",
    "detect_summary_rows_tool",
    "remove_duplicates_tool",
]


def register_tool(name, func):
    TOOL_REGISTRY[name] = func


def get_tools():
    """Return tools in explicit pipeline order. Skips any in PIPELINE_ORDER that aren't registered."""
    registry = TOOL_REGISTRY
    ordered = []
    for name in PIPELINE_ORDER:
        if name in registry:
            ordered.append((name, registry[name]))
    # Include any registered tools not in PIPELINE_ORDER (at end)
    for name, func in registry.items():
        if name not in PIPELINE_ORDER:
            ordered.append((name, func))
    return ordered
