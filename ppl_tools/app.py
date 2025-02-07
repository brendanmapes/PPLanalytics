import sys

from PySide6.QtWidgets import QMainWindow, QApplication

from ppl_tools.gui.airtable_upload.logic import AirtableUploadLogic
from ppl_tools.gui.main_window_ui import Ui_MainWindow
from ppl_tools.gui.clustering.logic import ClusterTab

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


        self.airtable_upload_logic = AirtableUploadLogic(self.ui)

        self.cluster_tab = ClusterTab()
        self.ui.tabWidget.insertTab(1, self.cluster_tab, "Cluster R3 Findings")
        self.ui.tabWidget.setCurrentIndex(0)

def run():
    q_app = QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(q_app.exec())
