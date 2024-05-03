"""
Created: 15-03-2024 20:18
Author: Anirudh
"""
import sys
import os
from pathlib import Path
from PyQt6 import QtWidgets
from mainWindow import MainWindow


if __name__ == '__main__':
    # Get template filepath
    try:
        template_path, text_path = sys.argv[1], sys.argv[2]

    except IndexError as e:
        CURRENT_DIRECTORY = Path(__file__).resolve().parent
        template_path = os.path.join(CURRENT_DIRECTORY/"resources"/"assets", "report.htm")
        text_path = os.path.join(CURRENT_DIRECTORY/"resources"/"assets", "report.txt")

    # Open Window
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.fillReport(template_path, text_path)
    app.exec()
