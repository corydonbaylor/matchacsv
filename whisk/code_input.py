# code_runner.py
import traceback
import pandas as pd
import siuba
from siuba import _, select, filter, mutate, summarize, group_by, arrange
siuba_available = True

from PySide6.QtWidgets import QPlainTextEdit, QPushButton, QHBoxLayout
from PySide6.QtGui import QShortcut, QKeySequence

def create_code_bar(window):
    """
    Top bar with a code editor and Run button.
    'window' is your QMainWindow (CSVEditor) that has df, table, update_table().
    """
    bar = QHBoxLayout()

    # Attach widgets onto the window for easy access elsewhere
    window.code_input = QPlainTextEdit()
    placeholder = (
        "Pandas code. 'df' is the current DataFrame.\n"
        "Examples:\n"
        "df = df.head(10)\n"
        "df['Total'] = pd.to_numeric(df[0], errors='coerce') + pd.to_numeric(df[1], errors='coerce')"
    )
    if siuba_available:
        placeholder += (
            "\n\nsiuba example:\n"
            "df2 = df >> filter_(_.col1 > 10) >> select(_.col1, _.col2)"
        )
    window.code_input.setPlaceholderText(placeholder)
    window.code_input.setFixedHeight(110)

    run_btn = QPushButton("Run (Ctrl+Enter)")
    run_btn.clicked.connect(lambda: run_code(window))

    # Keyboard shortcut
    QShortcut(QKeySequence("Ctrl+Return"), window, activated=lambda: run_code(window))

    bar.addWidget(window.code_input)
    bar.addWidget(run_btn)
    return bar


def create_output_box(window):
    """
    Bottom read-only output box where non-DataFrame results (or errors) appear.
    Call layout.addWidget(create_output_box(self)) in init_ui().
    """
    window.output_box = QPlainTextEdit()
    window.output_box.setReadOnly(True)
    window.output_box.setPlaceholderText("Output will appear here (non-DataFrame results, errors, logs).")
    window.output_box.setFixedHeight(140)
    return window.output_box


def _ensure_output_box(window):
    """Create an output box on-demand if caller forgot to add one."""
    if not hasattr(window, "output_box") or window.output_box is None:
        # Fallback: create a floating box if no layout reference is available.
        window.output_box = QPlainTextEdit(parent=window)
        window.output_box.setReadOnly(True)
        window.output_box.setFixedHeight(140)
        window.output_box.setWindowTitle("Output")
        window.output_box.show()


def _to_text(value):
    """Pretty-print helper for common pandas/py types."""
    try:
        import pandas as pd
        if isinstance(value, pd.DataFrame):
            return value.to_string(index=False)
        if isinstance(value, pd.Series):
            return value.to_string()
    except Exception:
        pass
    # Fallbacks
    try:
        return str(value)
    except Exception:
        return repr(value)


def _headerize(display_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the 'display' df (row 0 = header row) into a logical df whose
    columns come from row 0 and whose data starts at row 1.
    """
    if display_df is None or display_df.empty:
        return pd.DataFrame()
    cols = display_df.iloc[0].astype(str).tolist()
    data = display_df.iloc[1:].reset_index(drop=True)
    data.columns = cols
    return data

def _deheaderize(logical_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert a logical df with real column names back into the 'display' df
    where row 0 contains the column names and subsequent rows are data.
    """
    if logical_df is None:
        return pd.DataFrame([[]])
    header_row = pd.DataFrame([list(map(str, logical_df.columns))])
    body = logical_df.reset_index(drop=True)
    display = pd.concat([header_row, body], ignore_index=True)
    display = display.astype(str).fillna("")
    return display

def run_code(window):
    """
    Execute pandas code from the top text box directly against window.df.
    - If the result is a DataFrame (via eval or reassignment), adopt it.
    - Otherwise, render the result text in the bottom output box.
    - Errors are captured and shown in the bottom output box.
    """
    code = window.code_input.toPlainText().strip()
    if not code:
        return

    local_env = {"pd": pd, "df": window.df}
    if siuba_available:
        from siuba import _, select, filter, mutate, summarize, group_by, arrange
        local_env.update({
            "_": _,
            "select": select,
            "filter": filter,
            "mutate": mutate,
            "summarize": summarize,
            "group_by": group_by,
            "arrange": arrange
        })

    non_df_result = None

    try:
        # Try expression first (e.g., "df.head(10)" or "df.shape")
        try:
            result = eval(code, {}, local_env)
            if isinstance(result, pd.DataFrame):
                local_env["df"] = result
            else:
                non_df_result = result
        except SyntaxError:
            # Not an expression → run statements (e.g., "df = df.dropna()")
            exec(code, {}, local_env)

        # Did we end up with a DataFrame?
        new_df = local_env.get("df", None)
        if isinstance(new_df, pd.DataFrame):
            window.df = new_df
            window.update_table()
            _ensure_output_box(window)
            window.output_box.setPlainText(f"DataFrame updated. Shape: {window.df.shape}")
        else:
            # Show non-DataFrame result (or a helpful message) in bottom box
            _ensure_output_box(window)
            if non_df_result is not None:
                window.output_box.setPlainText(_to_text(non_df_result))
            else:
                window.output_box.setPlainText("No DataFrame produced and no evaluable result to display.")

    except Exception as e:
        _ensure_output_box(window)
        if not siuba_available and ("siuba" in code or "filter_" in code or "select" in code or "_" in code):
            window.output_box.setPlainText(
                "Error running code:\n"
                + str(e)
                + "\n\nIt looks like you are trying to use siuba but it is not installed.\n"
                + "Please install it with: pip install siuba"
            )
        else:
            window.output_box.setPlainText("Error running code:\n" + traceback.format_exc())