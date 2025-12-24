from pyobd.gui.coding_dialog import CodingDialog
...
self.menuBar().addAction("Factory Coding (VAG)", self.open_coding)
...
def open_coding(self):
    dlg = CodingDialog(self.connection, self)
    dlg.exec_()
