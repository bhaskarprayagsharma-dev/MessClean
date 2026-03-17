from modules.tool_registry import register_tool
from modules.semantic_detector import detect_semantic_type

def semantic_column_mapper(df, metadata):

    for col in df.columns:

        semantic = detect_semantic_type(df[col])

        metadata["columns"][col] = {
            "semantic_type": semantic
        }

    return df, metadata, metadata["columns"]


register_tool("semantic_column_mapper", semantic_column_mapper)
