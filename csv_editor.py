import sys
import pandas as pd
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QFileDialog,
                             QMessageBox, QHeaderView)
from PySide6.QtCore import Qt

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

class CSVEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df = None
        self.column_names = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("CSV Editor")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create table widget
        self.table = QTableWidget()
        self.table.setColumnCount(26)  # Start with 26 columns (A-Z)
        self.table.setHorizontalHeaderLabels(get_sheet_columns(26))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Create button layout
        button_layout = QHBoxLayout()

        # Create buttons
        open_button = QPushButton("Open CSV")
        save_button = QPushButton("Save CSV")
        add_row_button = QPushButton("Add Row")
        add_col_button = QPushButton("Add Column")
        del_row_button = QPushButton("Delete Row")
        del_col_button = QPushButton("Delete Column")

        # Add buttons to layout
        button_layout.addWidget(open_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(add_row_button)
        button_layout.addWidget(add_col_button)
        button_layout.addWidget(del_row_button)
        button_layout.addWidget(del_col_button)

        # Add button layout to main layout
        layout.addLayout(button_layout)

        # Connect signals
        open_button.clicked.connect(self.open_csv)
        save_button.clicked.connect(self.save_csv)
        add_row_button.clicked.connect(self.add_row)
        add_col_button.clicked.connect(self.add_column)
        del_row_button.clicked.connect(self.delete_row)
        del_col_button.clicked.connect(self.delete_column)

        # Connect table signals
        self.table.cellChanged.connect(self.handle_cell_change)

    def open_csv(self):
        """Open a CSV file and display its contents in the table."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_name:
            try:
                # Read CSV with header=None so the first row is treated as data
                self.df = pd.read_csv(file_name, header=None)
                self.column_names = list(self.df.columns)  # Store the column names
                self.update_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open CSV: {e}")

    def update_table(self):
        """Update the table widget to display the contents of the DataFrame."""
        if self.df is None:
            return
        num_rows = len(self.df)
        num_cols = len(self.df.columns)
        self.table.setRowCount(num_rows)
        self.table.setColumnCount(num_cols)
        self.table.setHorizontalHeaderLabels(get_sheet_columns(num_cols))
        for i in range(num_rows):
            for j in range(num_cols):
                item = QTableWidgetItem(str(self.df.iloc[i, j]))
                self.table.setItem(i, j, item)

    def save_csv(self):
        """Save the current table contents to a CSV file."""
        file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv)")
        if file_name:
            try:
                # Get data directly from the table widget
                data = []
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)
                
                # Convert to DataFrame and save without index
                df = pd.DataFrame(data)
                df.to_csv(file_name, index=False, header=False)
                QMessageBox.information(self, "Success", "File saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save CSV: {e}")

    def add_row(self):
        """Add a new row to the table."""
        current_row = self.table.currentRow()
        self.table.insertRow(current_row + 1 if current_row >= 0 else self.table.rowCount())

    def add_column(self):
        """Add a new column to the table."""
        current_col = self.table.currentColumn()
        new_col = current_col + 1 if current_col >= 0 else self.table.columnCount()
        self.table.insertColumn(new_col)
        self.table.setHorizontalHeaderLabels(get_sheet_columns(self.table.columnCount()))

    def delete_row(self):
        """Delete the selected row from the table."""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)

    def delete_column(self):
        """Delete the selected column from the table."""
        current_col = self.table.currentColumn()
        if current_col >= 0:
            self.table.removeColumn(current_col)
            self.table.setHorizontalHeaderLabels(get_sheet_columns(self.table.columnCount()))

    def handle_cell_change(self, row, column):
        """Handle changes to table cells."""
        if self.df is not None:
            item = self.table.item(row, column)
            if item is not None:
                self.df.iloc[row, column] = item.text()

def main():
    app = QApplication(sys.argv)
    editor = CSVEditor()
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 