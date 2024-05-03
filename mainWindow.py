"""
    Project Name: reportGeneratorCTS
    Author: S V Anirudh
    Date: 15-Mar-24 08:30 PM
"""
from pathlib import Path
import shutil
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QThreadPool, QTimer
from PyQt6.QtPdfWidgets import QPdfView
from PyQt6.QtPdf import QPdfDocument
from reportGenerator import Generator, Converter

CURRENT_DIRECTORY = Path(__file__).resolve().parent


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set up the application
        uic.loadUi(CURRENT_DIRECTORY / "resources" / "ui" / "mainWindow.ui", self)
        self.setWindowTitle("Report Generator")

        # Threadpool
        self.threadpool = QThreadPool()

        # Variables
        self.filePath = None
        self.html_template = None
        self.xml_values = None

        # Set status bar
        self._label = QtWidgets.QLabel()
        self.statusBar.addPermanentWidget(self._label, stretch=1)

        self._progress_bar = QtWidgets.QProgressBar()
        self._progress_bar.setFixedSize(self.geometry().width() - 320, 16)
        self._progress_bar.hide()
        self.statusBar.addPermanentWidget(self._progress_bar)

        self._label2 = QtWidgets.QLabel()
        self._label2.hide()
        self.statusBar.addPermanentWidget(self._label2)

        # Set the QPdfView
        self.pdfViewer = QPdfView(None)
        self.pdfViewer.setPageMode(QPdfView.PageMode.MultiPage)

        self.setCentralWidget(self.pdfViewer)

        # Set Connections
        self.actionRefresh.triggered.connect(self.fillReport)
        self.actionDownload.triggered.connect(self.downloadFile)

    def fillReport(self, html_template=None, text_values=None):
        """
        Gets the path of the html template file and xml value file
        Fills the report parameters in a html
        Runs in background
        Invokes pdf conversion after filling
        :param html_template: html path
        :param text_values: xml path
        :return:
        """
        # Get the file paths
        if html_template:
            self.html_template = html_template
        if text_values:
            self.xml_values = text_values

        # Set the name to the status bar
        self._label.setText(Path(self.html_template).stem)

        # Set the progressbar to statusbar
        self._progress_bar.show()
        self._progress_bar.setValue(0)

        # Generate report
        generator = Generator(self.html_template, self.xml_values)
        generator.signal.res.connect(self.convert_html_2_pdf)
        self.threadpool.start(generator)

    def convert_html_2_pdf(self, html_file):
        """
        Takes in the html file and convert it to the pdf
        :param html_file: str
        :return:
        """
        # Set progressbar value
        self._progress_bar.setValue(48)

        # Convert to html
        converter = Converter(html_file)
        converter.signal.res.connect(self.setFile)
        converter.run()

    def setFile(self, filepath):
        """
        Views the pdf file
        (Also a connection for refresh)
        :param filepath: template file path
        :return:
        """
        # Set progress bar values
        self._progress_bar.setValue(96)

        # Close existing pdfDocument
        if self.pdfViewer.document():
            self.pdfViewer.document().close()

        # Load the document
        self.filePath = filepath
        document = QPdfDocument(self)
        document.load(filepath)

        # Set the file
        self.pdfViewer.setDocument(document)

        # Set Progress bar
        self._progress_bar.setValue(100)
        self._progress_bar.hide()

    def downloadFile(self):
        """
        Downloads the file in the desired location
        :return:
        """
        # Set progress bar
        self._progress_bar.show()
        self._progress_bar.setValue(20)

        path_to_save = QtWidgets.QFileDialog.getSaveFileName(parent=self,
                                                             caption="Download",
                                                             filter="PDF (*.pdf)")
        if len(path_to_save[0]):
            shutil.copyfile(self.filePath, path_to_save[0])

            # Set progress bar
            self._progress_bar.setValue(100)
            self._progress_bar.hide()
            self._label2.setText("Downloaded")
            self._label2.show()
            QTimer.singleShot(2500, self._label2.hide)

        else:
            # Set progress bar
            self._progress_bar.setValue(0)
            self._progress_bar.hide()
            self._label2.setText("Cancelled")
            self._label2.show()
            QTimer.singleShot(2500, self._label2.hide)
