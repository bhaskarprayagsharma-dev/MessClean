import pandas as pd


def ensure_unique_column_names(df):
    """
    Rename duplicate column names so each is unique. Returns (df, renames)
    where renames is a list of (old_name, new_name) for columns that were renamed.
    """
    renames = []
    new_columns = []
    seen = {}

    for col in df.columns:
        if col in seen:
            seen[col] += 1
            new_name = f"{col}_{seen[col]}"
            renames.append((col, new_name))
            new_columns.append(new_name)
        else:
            seen[col] = 1  # count of occurrences so far
            new_columns.append(col)

    if not renames:
        return df, []

    df = df.copy()
    df.columns = new_columns
    return df, renames


def read_excel(file, sheet_name=None):
    if sheet_name:
        df = pd.read_excel(file, sheet_name=sheet_name)
        return {sheet_name: df}

    sheets = pd.read_excel(file, sheet_name=None)
    return sheets
