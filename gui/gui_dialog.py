import sys
import threading
from PyQt5.QtWidgets import QApplication, QMessageBox


class DispatchMsgBox(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.msg_box = None
        self.app = app

    def run(self):
        app = self.app
        self.msg_box = QMessageBox()
        self.msg_box.setText('Dispatch in progress. \n'
                             'Window will close automatically once dispatch is finished')
        self.msg_box.exec_()
