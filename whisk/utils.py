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