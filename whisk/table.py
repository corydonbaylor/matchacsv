from PySide6.QtWidgets import (QTableWidget, QHeaderView)
import whisk

def setup_table():       
        # Create table widget
        table = QTableWidget()
        # we create 26 columns (A-Z) initially
        table.setColumnCount(26)  
        # we then use the get_sheet_columns function to set the headers
        table.setHorizontalHeaderLabels(whisk.get_sheet_columns(26))
        # Set the table to stretch to fill the window
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        # add self.table to the layout
        return table