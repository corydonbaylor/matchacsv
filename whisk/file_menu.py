# file_menu.py
from PySide6.QtGui import QAction
import pandas as pd
from PySide6.QtWidgets import QFileDialog, QMessageBox
import whisk

def setup_file_menu(window):
    """Attach a File menu to the given QMainWindow and wire handlers."""
    # what is window? It is an instance of the application
    # we use attributes of the app to create a menu bar
    menu_bar = window.menuBar() # this is a class from that instance
    file_menu = menu_bar.addMenu("File")

    # we add these actions to the file menui
    open_action = QAction("Open CSV", window)
    save_action = QAction("Save CSV", window)

    # and we create shortcuts for these actions
    open_action.setShortcut("Ctrl+O")
    save_action.setShortcut("Ctrl+S")

    # we then connect the actions to their respective functions
    open_action.triggered.connect(lambda: open_csv(window))
    save_action.triggered.connect(lambda: save_csv(window))

    # finally, we add the actions to the file menu
    file_menu.addAction(open_action)
    file_menu.addAction(save_action)

    # which is what we return
    return file_menu

def open_csv(window):
    """Open a CSV file and display its contents in the table."""
    file_name, _ = QFileDialog.getOpenFileName(window, "Open CSV File", "", "CSV Files (*.csv)")
    if file_name:
        try:
            # Read CSV with header=None so the first row is treated as data
            # A/B/C visual headers will be set by the table, not stored in df
            window.df = pd.read_csv(file_name, header=0, dtype=str, keep_default_na=False)
            window.update_table()
            print(window.df)
        except Exception as e:
            QMessageBox.critical(window, "Error", f"Failed to open CSV: {e}")

def save_csv(window):
    """Save only populated rows/columns to CSV."""
    file_name, _ = QFileDialog.getSaveFileName(window, "Save CSV File", "", "CSV Files (*.csv)")
    if not file_name:
        return
    try:
        # Pull data from the table
        data = []
        for r in range(window.table.rowCount()):
            row = []
            for c in range(window.table.columnCount()):
                item = window.table.item(r, c)
                row.append(item.text() if item else "")
            data.append(row)

        df = pd.DataFrame(data)

        df = whisk.filter_non_empty(df)

        # Optionally: if everything was empty, write an empty file
        if df.empty:
            df = pd.DataFrame()

        df.to_csv(file_name, index=False, header=False)
        QMessageBox.information(window, "Success", "File saved successfully!")
    except Exception as e:
        QMessageBox.critical(window, "Error", f"Failed to save CSV: {e}")