"""
Minimal PyQt5 dialog: read → edit hex → write long-coding.
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from obd.coding.coding_commands import install_coding_cmds

class CodingDialog(QDialog):
    def __init__(self, connection, parent=None):
        super().__init__(parent)
        self.conn = connection
        self.setWindowTitle("Factory Coding (VAG) – Amarok")
        self.resize(600, 120)

        v = QVBoxLayout(self)
        v.addWidget(QLabel("Long coding (30 bytes hex):"))
        self.edit = QLineEdit()
        self.edit.setMaxLength(60)   # 30 bytes = 60 hex chars
        self.edit.setText("00" * 30)
        v.addWidget(self.edit)

        h = QHBoxLayout()
        self.read_btn  = QPushButton("Read from ECU")
        self.write_btn = QPushButton("Write to ECU")
        h.addWidget(self.read_btn)
        h.addWidget(self.write_btn)
        v.addLayout(h)

        self.read_btn.clicked.connect(self.read_coding)
        self.write_btn.clicked.connect(self.write_coding)

    # ------------------------------------------------------------------
    def read_coding(self):
        install_coding_cmds(self.conn, 0x09)      # BCM
        resp = self.conn.query("ReadLongCoding")
        if resp.is_null():
            QMessageBox.critical(self, "Error", "Read failed – check adapter/ECU")
            return
        hex_str = resp.value.hex().upper()
        self.edit.setText(hex_str)

    def write_coding(self):
        hex_str = self.edit.text().replace(" ", "")
        if len(hex_str) != 60:
            QMessageBox.warning(self, "Format", "Need exactly 60 hex chars (30 bytes)")
            return
        new_bytes = bytes.fromhex(hex_str)
        install_coding_cmds(self.conn, 0x09)
        cmd = self.conn.supported_commands["WriteLongCoding"]
        cmd.data = new_bytes
        resp = self.conn.query(cmd)
        if resp.is_null():
            QMessageBox.critical(self, "Error", "Write failed – security or checksum")
        else:
            QMessageBox.information(self, "Success", "Coding written – cycle ignition to apply.")
