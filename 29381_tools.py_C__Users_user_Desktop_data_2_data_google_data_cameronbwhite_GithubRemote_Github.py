from PyQt4.QtGui import QApplication, QCursor
from PyQt4.QtCore import Qt

def waiting_effects(function):
    def new_function(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        result = function(self)
        QApplication.restoreOverrideCursor()
        return result
    return new_function

