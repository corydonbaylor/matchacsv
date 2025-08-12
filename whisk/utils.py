def get_sheet_columns(n):
    """Generate Excel-style column names (A, B, C, ..., Z, AA, AB, ...)"""
    result = []
    for i in range(n):
        col = ""
        while i >= 0:
            col = chr(65 + (i % 26)) + col
            i = i // 26 - 1
        result.append(col)
    return result

import pandas as pd

def filter_non_empty(df):
    """
    Keep only columns and rows with at least one non-empty value.
    """
    # Treat empty strings or whitespace as NaN
    df = df.replace(r'^\s*$', pd.NA, regex=True)
    
    # --- COLUMN FILTER ---
    # Keep only columns where at least one value is NOT NaN
    df = df.dropna(axis=1, how='all')
    
    # --- ROW FILTER ---
    # Keep only rows where at least one value is NOT NaN
    df = df.dropna(axis=0, how='all')
    
    return df