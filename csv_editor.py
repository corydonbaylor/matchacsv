import sys
import pandas as pd
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QFileDialog,
                             QMessageBox, QHeaderView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction  # <-- QAction is here in Qt6

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
    """A simple CSV editor using PySide6 and pandas."""
    def __init__(self):
        super().__init__()
        self.df = pd.DataFrame(
            [["" for _ in range(26)] for _ in range(100)],  # 100 rows, 26 columns
            columns=get_sheet_columns(26)
        )
        self.column_names = list(self.df.columns)
        self.init_ui() # calls the below method to set up the UI

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("MatchaCSV")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and layout
        ## this creates a blank canvas for the main window
        central_widget = QWidget()
        ## this tells the main window to use the central widget
        ## anything you want to show inside the main window will go inside this widget 
        self.setCentralWidget(central_widget)

        # we will use a vertical layout to stack the table and buttons
        layout = QVBoxLayout(central_widget)

        ##~~~~ CREATE TABLE WIDGET ~~~##
        # Create table widget
        self.table = QTableWidget()
        # we create 26 columns (A-Z) initially
        self.table.setColumnCount(26)  
        # we then use the get_sheet_columns function to set the headers
        self.table.setHorizontalHeaderLabels(get_sheet_columns(26))
        # Set the table to stretch to fill the window
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # add self.table to the layout
        layout.addWidget(self.table)
        self.update_table()

        ##~~~~ CREATE MENU ~~~##
        # first we are going to create a menu bar
        menu_bar = self.menuBar()
        # then we add a "File" menu to the menu bar
        file_menu = menu_bar.addMenu("File")

        # Create actions for File menu
        open_action = QAction("Open CSV", self)
        save_action = QAction("Save CSV", self)

        # Connect actions to methods
        open_action.triggered.connect(self.open_csv)
        save_action.triggered.connect(self.save_csv)

        # Add actions to File menu
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

        ##~~~~ CREATE BUTTONS WIDGET ~~~##
        # Create button layout
        button_layout = QHBoxLayout()

        # Create buttons
        add_row_button = QPushButton("Add Row")
        add_col_button = QPushButton("Add Column")
        del_row_button = QPushButton("Delete Row")
        del_col_button = QPushButton("Delete Column")

        # Add buttons to layout
        button_layout.addWidget(add_row_button)
        button_layout.addWidget(add_col_button)
        button_layout.addWidget(del_row_button)
        button_layout.addWidget(del_col_button)

        # Add button layout to main layout
        layout.addLayout(button_layout)

        # Connect signals
        add_row_button.clicked.connect(self.add_row)
        add_col_button.clicked.connect(self.add_column)
        del_row_button.clicked.connect(self.delete_row)
        del_col_button.clicked.connect(self.delete_column)

        # Connect table signals
        # each time a cell is changed, we will call the handle_cell_change method
        # this includes the row and column indices of the changed cell
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
        if self.df is None:
            return
        self.table.blockSignals(True)
        num_rows, num_cols = len(self.df), len(self.df.columns)
        self.table.setRowCount(num_rows)
        self.table.setColumnCount(num_cols)
        self.table.setHorizontalHeaderLabels(get_sheet_columns(num_cols))
        for i in range(num_rows):
            for j in range(num_cols):
                self.table.setItem(i, j, QTableWidgetItem(str(self.df.iloc[i, j])))
        self.table.blockSignals(False)

    def save_csv(self):
        """Save only populated rows/columns to CSV."""
        file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv)")
        if not file_name:
            return
        try:
            # Pull data from the table
            data = []
            for r in range(self.table.rowCount()):
                row = []
                for c in range(self.table.columnCount()):
                    item = self.table.item(r, c)
                    row.append(item.text() if item else "")
                data.append(row)

            df = pd.DataFrame(data)

            # Treat "", None, or whitespace-only as empty; then drop all-empty rows/cols
            df = df.applymap(lambda x: pd.NA if (x is None or (isinstance(x, str) and x.strip() == "")) else x)
            df = df.dropna(how="all")            # drop empty rows
            df = df.dropna(axis=1, how="all")    # drop empty columns

            # Optionally: if everything was empty, write an empty file
            if df.empty:
                df = pd.DataFrame()

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
        # checks if dataframe exists
        if self.df is not None:
            # returns qtablewidgetitem at the specified row and column
            # if the item is not None, it updates the DataFrame with the new text
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