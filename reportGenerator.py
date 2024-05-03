"""
    Project Name: reportGeneratorCTS
    Author: S V Anirudh
    Date: 17-Mar-24 05:30 PM
"""
import os
import re
from pathlib import Path
from PyQt6 import QtCore
from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
from PyQt6.QtWebEngineWidgets import QWebEngineView

CURRENT_DIRECTORY = Path(__file__).resolve().parent


class WorkerSignals(QObject):
    """
    The signals associated with the worker thread
    """
    res = pyqtSignal(str)


class Generator(QRunnable):
    """
    Worker Thread
    Creates a copy of the template html and fills the values
    """

    def __init__(self, html_template, text_values):
        super().__init__()
        self.html_template = html_template
        self.text_values = text_values
        self.filled_html = os.path.join(CURRENT_DIRECTORY/"outputs", Path(self.html_template).stem + ".html")
        self.signal = WorkerSignals()

    def generate_html(self, content, data):
        def repl(match):
            key = match.group(0)
            return data.get(key, key)

        pattern = re.compile(r'@%\d+', re.IGNORECASE)
        content = pattern.sub(repl, content)

        return content

    @pyqtSlot()
    def run(self):
        """
        Fills the values
        :return:
        """
        # Read the html content
        with open(self.html_template, "r") as f:
            content = f.read()
        f.close()

        # Read the data content
        with open(self.text_values, "r") as f:
            data = {}
            for line in f.readlines():
                sample = line.rstrip('\n').split(" ")
                data[sample[0]] = sample[1]
        f.close()

        # Write it a html file
        with open(self.filled_html, "w") as f:
            f.write(self.generate_html(content, data))
        f.close()

        # Send the filled html file as the signal
        self.signal.res.emit(self.filled_html)


class Converter(QRunnable):
    """
    Worker Thread
    Converts the given html file into pdf
    """

    def __init__(self, html_file):
        self.html_file = html_file
        self.signal = WorkerSignals()

    def run(self):
        """
        Converts the html file into pdf
        :return:
        """
        # Load the html file
        view = QWebEngineView(None)
        view.load(QtCore.QUrl.fromLocalFile(self.html_file))

        # Save
        output_file = os.path.join(CURRENT_DIRECTORY / "outputs", Path(self.html_file).stem + ".pdf")
        view.loadFinished.connect(lambda x: view.printToPdf(output_file))
        view.pdfPrintingFinished.connect(lambda x: self.signal.res.emit(output_file))
