from PyQt5.QtWidgets import QApplication
from connecttopi import PiLoginWidget
from SeqWidget import SchedulerGUI
import sys

class AppManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.scheduler_window = None  # Keep reference here

        self.login_window = PiLoginWidget()
        self.login_window.login_successful.connect(self.launch_scheduler)
        self.login_window.show()

    def launch_scheduler(self, ssh_client):
        self.scheduler_window = SchedulerGUI(ssh_client)
        self.scheduler_window.show()

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app_manager = AppManager()
    app_manager.run()
