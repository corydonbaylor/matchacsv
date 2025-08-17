from PySide6.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem
from PySide6.QtGui import QUndoStack, QUndoCommand
import pandas as pd
import whisk


class CellEditCommand(QUndoCommand):
    """Undoable command for a single cell edit in SpreadsheetTable."""
    def __init__(self, table: 'SpreadsheetTable', row: int, col: int, old_value, new_value):
        super().__init__(f"Edit cell ({row+1}, {col+1})")
        self._table = table
        self._row = row
        self._col = col
        self._old = old_value
        self._new = new_value

    def undo(self):
        self._table._apply_cell_value(self._row, self._col, self._old)

    def redo(self):
        self._table._apply_cell_value(self._row, self._col, self._new)


class Table(QTableWidget):
    """
    Spreadsheet-style table that renders a pandas DataFrame
    and supports undo/redo for single cell edits.
    """
    def __init__(self, columns: int = 26, parent=None):
        super().__init__(parent)
        self._df: pd.DataFrame | None = None
        self._undo_stack = QUndoStack(self)
        self._suppress_changes = False

        # Initial visual setup (A..Z default headers)
        self.setColumnCount(columns)
        self.setHorizontalHeaderLabels(whisk.get_sheet_columns(columns))
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # Listen for user edits
        self.cellChanged.connect(self._on_cell_changed)

    # ---------- public API ----------

    def set_dataframe(self, df: pd.DataFrame) -> None:
        """Render a DataFrame into the table and keep a reference for syncing edits."""
        self._df = df
        if df is None:
            return

        self.blockSignals(True)
        rows, cols = df.shape
        self.setRowCount(rows)
        self.setColumnCount(cols)
        self.setHorizontalHeaderLabels([str(c) for c in df.columns])

        for r in range(rows):
            for c in range(cols):
                self.setItem(r, c, QTableWidgetItem(str(df.iat[r, c])))
        self.blockSignals(False)

    def undo(self):
        """Convenience wrapper to trigger undo."""
        self._undo_stack.undo()

    def redo(self):
        """Convenience wrapper to trigger redo."""
        self._undo_stack.redo()

    def undo_stack(self) -> QUndoStack:
        """Expose the stack if you want to wire menu actions/shortcuts."""
        return self._undo_stack

    # ---------- internals ----------

    def _apply_cell_value(self, row: int, col: int, value):
        """Apply to both DataFrame and widget without re-triggering signals."""
        if self._df is None:
            return
        try:
            self._suppress_changes = True
            # update model
            self._df.iloc[row, col] = value
            # update view
            item = self.item(row, col)
            if item is None:
                self.setItem(row, col, QTableWidgetItem(str(value)))
            else:
                item.setText(str(value))
        finally:
            self._suppress_changes = False

    def _on_cell_changed(self, row: int, column: int):
        """When a user edits a cell, push an undoable command."""
        if self._df is None or self._suppress_changes:
            return
        item = self.item(row, column)
        if item is None:
            return

        new_val = item.text()
        old_val = self._df.iloc[row, column]
        if str(old_val) == new_val:
            return  # no effective change

        # Push command; per Qt design, pushing executes redo() immediately.
        self._undo_stack.push(CellEditCommand(self, row, column, old_val, new_val))