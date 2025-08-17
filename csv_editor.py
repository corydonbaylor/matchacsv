import sys
import pandas as pd
from PySide6.QtWidgets import (QApplication, QMainWindow, 
                             QVBoxLayout, QHBoxLayout, QWidget, QPushButton, 
                             )
import whisk
from PySide6.QtGui import QKeySequence

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
        
        layout.addLayout(whisk.create_code_bar(self))
        layout.addWidget(whisk.create_output_box(self))

        ##~~~~ CREATE TABLE WIDGET ~~~##
        self.table = whisk.Table(parent=self)
        layout.addWidget(self.table)
        # render current DataFrame
        self.table.set_dataframe(self.df)
        
        # Create actions from the table’s undo stack
        undo_action = self.table.undo_stack().createUndoAction(self, "Undo")
        redo_action = self.table.undo_stack().createRedoAction(self, "Redo")

        # Standard shortcuts (Qt maps Ctrl to ⌘ on macOS)
        undo_action.setShortcut(QKeySequence.Undo)
        redo_action.setShortcuts([QKeySequence.Redo, QKeySequence("Ctrl+Shift+Z")])

        # Make the window listen for these shortcuts
        self.addAction(undo_action)
        self.addAction(redo_action)
        ##~~~~ SETUP FILE MENU ~~~##
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

    # this is used to pass the df from the main class to the table class
    def update_table(self):
        if self.df is None:
            return
        self.table.set_dataframe(self.df)


    def add_row(self):
        """Add a new row to the table."""
        current_row = self.table.currentRow()
        self.table.insertRow(current_row + 1 if current_row >= 0 else self.table.rowCount())

    def add_column(self):
        """Add a new column to the table."""
        current_col = self.table.currentColumn()
        new_col = current_col + 1 if current_col >= 0 else self.table.columnCount()
        self.table.insertColumn(new_col)
        self.table.setHorizontalHeaderLabels([str(c) for c in self.df.columns])

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
            self.table.setHorizontalHeaderLabels([str(c) for c in self.df.columns])

def main():
    app = QApplication(sys.argv)
    editor = CSVEditor()
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 