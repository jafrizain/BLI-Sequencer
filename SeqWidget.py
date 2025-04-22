import subprocess
import os
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox, QHBoxLayout, QComboBox, QLineEdit, QLabel
)
import json
import sys
from paramiko import SSHClient
from scp import SCPClient
import threading

class SchedulerGUI(QWidget):
    def __init__(self, ssh_tunnel):
        super().__init__()
        self.ssh_tunnel = ssh_tunnel
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Imaging Scheduler")
        self.setGeometry(100, 100, 800, 500)

        layout = QVBoxLayout()

        self.folder_label = QLabel("Save Folder: Not Selected")
        layout.addWidget(self.folder_label)

        self.select_folder_button = QPushButton("Select Save Folder")
        self.select_folder_button.clicked.connect(self.select_folder)
        layout.addWidget(self.select_folder_button)

        self.rootname_label = QLabel("Root Name:")
        layout.addWidget(self.rootname_label)

        self.rootname_input = QLineEdit()
        layout.addWidget(self.rootname_input)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([ 
            "Step",
            "Exposure Time (s) or Macro File",
            "Mode",
            "Repetitions",
            "Interval (s)"
        ])
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Step")
        self.add_button.clicked.connect(self.add_step)
        button_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove Step")
        self.remove_button.clicked.connect(self.remove_step)
        button_layout.addWidget(self.remove_button)

        self.save_button = QPushButton("Save Schedule")
        self.save_button.clicked.connect(self.save_schedule)
        button_layout.addWidget(self.save_button)

        self.load_button = QPushButton("Load Schedule")
        self.load_button.clicked.connect(self.load_schedule)
        button_layout.addWidget(self.load_button)

        self.start_button = QPushButton("Start Acquisition")
        self.start_button.clicked.connect(self.start_acquisition)
        button_layout.addWidget(self.start_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.save_folder = ""

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Folder")
        if folder:
            self.save_folder = folder
            self.folder_label.setText(f"Save Folder: {folder}")

    def add_step(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        self.table.setItem(row, 1, QTableWidgetItem("1.0"))

        mode_dropdown = QComboBox()
        mode_dropdown.addItems(["Brightfield", "Darkfield", "Macro"])
        mode_dropdown.currentIndexChanged.connect(lambda: self.update_macro_selection(row, mode_dropdown))
        self.table.setCellWidget(row, 2, mode_dropdown)

        self.table.setItem(row, 3, QTableWidgetItem("1"))  # Repetitions
        self.table.setItem(row, 4, QTableWidgetItem("1"))  # Interval

    def update_macro_selection(self, row, combo):
        if combo.currentText() == "Macro":
            macro_file, _ = QFileDialog.getOpenFileName(self, "Select ImageJ Macro", "", "ImageJ Macros (*.ijm)")
            if macro_file:
                self.table.setItem(row, 1, QTableWidgetItem(macro_file))
            else:
                combo.setCurrentIndex(0)

    def remove_step(self):
        selected = self.table.currentRow()
        if selected >= 0:
            self.table.removeRow(selected)

    def save_schedule(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Schedule", "", "JSON Files (*.json)")
        if filename:
            schedule = {
                "save_folder": self.save_folder,
                "root_name": self.rootname_input.text(),
                "steps": []
            }
            for row in range(self.table.rowCount()):
                mode_widget = self.table.cellWidget(row, 2)
                mode = mode_widget.currentText() if mode_widget is not None else ""
                value = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
                repetitions = self.table.item(row, 3).text() if self.table.item(row, 3) else "1"
                interval = self.table.item(row, 4).text() if self.table.item(row, 4) else "1"

                step = {
                    "step": self.table.item(row, 0).text(),
                    "mode": mode,
                    "repetitions": repetitions,
                    "interval": interval
                }

                if mode == "Macro":
                    step["macro_file"] = value
                else:
                    step["exposure_time"] = value

                schedule["steps"].append(step)

            with open(filename, 'w') as file:
                json.dump(schedule, file)

    def load_schedule(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load Schedule", "", "JSON Files (*.json)")
        if filename:
            try:
                with open(filename, 'r') as file:
                    schedule = json.load(file)

                self.table.setRowCount(0)
                self.rootname_input.setText(schedule.get("root_name", ""))
                self.save_folder = schedule.get("save_folder", "")
                self.folder_label.setText(f"Save Folder: {self.save_folder or 'Not Selected'}")

                for idx, step in enumerate(schedule.get("steps", [])):
                    self.table.insertRow(idx)
                    self.table.setItem(idx, 0, QTableWidgetItem(str(step.get("step", idx + 1))))

                    mode_dropdown = QComboBox()
                    mode_dropdown.addItems(["Brightfield", "Darkfield", "Macro"])
                    self.table.setCellWidget(idx, 2, mode_dropdown)

                    if step["mode"] == "Macro":
                        self.table.setItem(idx, 1, QTableWidgetItem(step.get("macro_file", "")))
                        mode_dropdown.setCurrentText("Macro")
                    else:
                        self.table.setItem(idx, 1, QTableWidgetItem(step.get("exposure_time", "1.0")))
                        mode_dropdown.setCurrentText(step["mode"])

                    self.table.setItem(idx, 3, QTableWidgetItem(step.get("repetitions", "1")))
                    self.table.setItem(idx, 4, QTableWidgetItem(step.get("interval", "1")))

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load schedule:\n{str(e)}")

    def start_acquisition(self):
        root_name = self.rootname_input.text().strip()
        if not root_name:
            QMessageBox.critical(self, "Error", "Root Name is required.")
            return
        if not self.save_folder:
            QMessageBox.critical(self, "Error", "Save folder is not selected.")
            return
        num_steps = self.table.rowCount()
        if num_steps == 0:
            QMessageBox.critical(self, "Error", "No steps in schedule.")
            return

        for row in range(num_steps):
            mode_widget = self.table.cellWidget(row, 2)
            mode = mode_widget.currentText() if mode_widget else ""
            value = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
            repetitions = int(self.table.item(row, 3).text()) if self.table.item(row, 3) else 1
            interval = self.table.item(row, 4).text() if self.table.item(row, 4) else "1"
            directory = f"mkdir -p ~/Captures/{root_name}"
            stdin, stdout, stderr = self.ssh_tunnel.exec_command(directory)
            stdout.channel.recv_exit_status()  # Wait until it's done
            for i in range(repetitions):
                filename = f"{root_name}_{mode.lower()}_{i}"
                remote_path = f"~/Captures/{root_name}/{filename}"
                print(mode)
                print(value)
                print(remote_path)
                if mode == "Brightfield":
                    cmd = f"python3 brightfield.py {value} {remote_path}"
                elif mode == "Darkfield":
                    cmd = f"python3 darkfield.py {value} {remote_path}"
                else:
                    continue

                # Execute acquisition remotely
                stdin, stdout, stderr = self.ssh_tunnel.exec_command(cmd)
                stdout.channel.recv_exit_status()  # Wait until it's done

                # Fetch file immediately
                try:
                    with SCPClient(self.ssh_tunnel.get_transport()) as scp:
                        scp.get(remote_path + ".jpg", self.save_folder)
                        scp.get(remote_path + ".dng", self.save_folder)
                        
                except Exception as scp_error:
                    QMessageBox.warning(self, "Transfer Error", f"Failed to fetch {filename}: {scp_error}")

                # Sleep for interval
                time.sleep(float(interval))

