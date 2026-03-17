"""
Shared structure for tool detection results. Each tool returns proposed changes
with before/after previews; user approves per column or per row before apply.
"""


def make_change_id(tool_name, target):
    """Unique ID for a proposed change, used for approval tracking."""
    if isinstance(target, list):
        target = "_".join(str(t) for t in target[:5])  # cap for long lists
    return f"{tool_name}::{target}"


def parse_change_id(change_id):
    """Parse change_id back into (tool_name, target)."""
    if "::" in change_id:
        tool, target = change_id.split("::", 1)
        return tool, target
    return None, None
