import sys
import pandas as pd
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMessageBox
from PyQt6.QtGui import QFont, QKeyEvent
from PyQt6.QtCore import Qt

# Helper function to get column label for a given number (e.g., 1 -> 'A', 27 -> 'AA')
def get_column_labels(n):
    labels = []
    while n > 0:
        n, rem = divmod(n - 1, 26)
        labels.append(chr(65 + rem))
    return ''.join(reversed(labels))

# Helper function to generate a list of column labels (e.g., ['A', 'B', ..., 'Z'])
def get_sheet_columns(num):
    labels = []
    for i in range(1, num + 1):
        label = ''
        n = i
        while n > 0:
            n, rem = divmod(n - 1, 26)
            label = chr(65 + rem) + label
        labels.append(label)
    return labels

class CSVEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Editor")  # Set window title
        self.setGeometry(100, 100, 800, 600)  # Set window size and position
        self.df = None  # DataFrame to hold CSV data
        self.column_names = None  # Store column names from CSV

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create table widget for displaying/editing CSV data
        self.table = QTableWidget()
        self.table.setFont(QFont("Arial", 10))  # Set table font
        layout.addWidget(self.table)

        # Create 'Open CSV' button
        open_button = QPushButton("Open CSV")
        open_button.setFont(QFont("Arial", 10))
        open_button.clicked.connect(self.open_csv)  # Connect button to open_csv method
        layout.addWidget(open_button)

        # Create 'Save CSV' button
        save_button = QPushButton("Save CSV")
        save_button.setFont(QFont("Arial", 10))
        save_button.clicked.connect(self.save_csv)  # Connect button to save_csv method
        layout.addWidget(save_button)

        # Set stylesheet for appearance
        self.setStyleSheet("""
            QTableWidget {
                background-color: #f0f0f0;
                gridline-color: #d0d0d0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        # Show a blank sheet (A-Z columns, 1000 rows) by default
        self.show_blank_sheet()

    def show_blank_sheet(self):
        """Display a blank sheet with columns A-Z and 1000 rows, like Google Sheets."""
        num_cols = 26  # Number of columns (A-Z)
        num_rows = 1000  # Number of rows
        self.table.setRowCount(num_rows)
        self.table.setColumnCount(num_cols)
        self.table.setHorizontalHeaderLabels(get_sheet_columns(num_cols))  # Set column headers
        self.table.setVerticalHeaderLabels([str(i+1) for i in range(num_rows)])  # Set row numbers
        # Fill all cells with empty strings
        for i in range(num_rows):
            for j in range(num_cols):
                self.table.setItem(i, j, QTableWidgetItem(""))
        self.column_names = get_sheet_columns(num_cols)

    def open_csv(self):
        """Open a CSV file and display its contents in the table."""
        # ALL CAPS: THIS IS WHERE WE LOAD IN THE CSV FILE
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
        # ALL CAPS: THIS IS WHERE THE FIRST ROW OF THE CSV IS REMOVED FROM THE HEADER AND SHOWN AS DATA IN THE UI
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

    def keyPressEvent(self, event: QKeyEvent):
        """Handle arrow key navigation in the table."""
        if event.key() == Qt.Key.Key_Up:
            current_row = self.table.currentRow()
            if current_row > 0:
                self.table.setCurrentCell(current_row - 1, self.table.currentColumn())
        elif event.key() == Qt.Key.Key_Down:
            current_row = self.table.currentRow()
            if current_row < self.table.rowCount() - 1:
                self.table.setCurrentCell(current_row + 1, self.table.currentColumn())
        elif event.key() == Qt.Key.Key_Left:
            current_col = self.table.currentColumn()
            if current_col > 0:
                self.table.setCurrentCell(self.table.currentRow(), current_col - 1)
        elif event.key() == Qt.Key.Key_Right:
            current_col = self.table.currentColumn()
            if current_col < self.table.columnCount() - 1:
                self.table.setCurrentCell(self.table.currentRow(), current_col + 1)
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    # Start the Qt application
    app = QApplication(sys.argv)
    window = CSVEditor()
    window.show()
    sys.exit(app.exec()) 