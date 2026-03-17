def validate_file(uploaded_file):
    """Validate file size and that the file is readable Excel. Resets stream on success."""
    if uploaded_file.size > 50 * 1024 * 1024:
        return False, "File too large (max 50MB)."

    try:
        import pandas as pd
        pd.read_excel(uploaded_file, sheet_name=0)
        uploaded_file.seek(0)
        return True, ""
    except Exception as e:
        return False, f"Invalid or corrupted Excel file: {str(e)[:200]}"
