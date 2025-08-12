import sys
import pandas as pd
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QFileDialog,
                             QMessageBox, QHeaderView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction  # <-- QAction is here in Qt6
import whisk

class CSVEditor(QMainWindow):
    """A simple CSV editor using PySide6 and pandas."""
    def __init__(self):
        super().__init__()
        self.df = pd.DataFrame(
            [["" for _ in range(26)] for _ in range(100)],  # 100 rows, 26 columns
            columns=whisk.get_sheet_columns(26)
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
        self.table = whisk.setup_table()
        
        # add self.table to the layout
        layout.addWidget(self.table)
        self.update_table()

        whisk.setup_file_menu(self)

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

    def update_table(self):
        if self.df is None:
            return
        self.table.blockSignals(True)
        num_rows, num_cols = len(self.df), len(self.df.columns)
        self.table.setRowCount(num_rows)
        self.table.setColumnCount(num_cols)
        self.table.setHorizontalHeaderLabels(whisk.get_sheet_columns(num_cols))
        for i in range(num_rows):
            for j in range(num_cols):
                self.table.setItem(i, j, QTableWidgetItem(str(self.df.iloc[i, j])))
        self.table.blockSignals(False)


    def add_row(self):
        """Add a new row to the table."""
        current_row = self.table.currentRow()
        self.table.insertRow(current_row + 1 if current_row >= 0 else self.table.rowCount())

    def add_column(self):
        """Add a new column to the table."""
        current_col = self.table.currentColumn()
        new_col = current_col + 1 if current_col >= 0 else self.table.columnCount()
        self.table.insertColumn(new_col)
        self.table.setHorizontalHeaderLabels(whisk.get_sheet_columns(self.table.columnCount()))

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
            self.table.setHorizontalHeaderLabels(whisk.get_sheet_columns(self.table.columnCount()))

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