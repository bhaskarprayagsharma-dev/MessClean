def initialize_metadata():
    return {
        "columns": {},
        "operations": []
    }

def add_column_metadata(metadata, column, info):
    metadata["columns"][column] = info

def add_operation(metadata, operation):
    metadata["operations"].append(operation)
