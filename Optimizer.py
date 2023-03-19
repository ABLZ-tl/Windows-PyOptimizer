import os
import sys
import winreg
import win32con
import winshell
import subprocess

from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QVBoxLayout, QFileDialog, QMessageBox, QStyleFactory
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class Worker(QThread):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        self.manage_startup_programs()
        self.finished.emit()

    def manage_startup_programs(self):
        # Gestionar programas de inicio
        try:
            startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
            for file_name in os.listdir(startup_folder):
                file_path = os.path.join(startup_folder, file_name)
                if file_path.endswith('.lnk'):
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_ALL_ACCESS) as reg_key:
                        app_name = file_name.split('.')[0]
                        app_path = file_path.replace('\\', '/')
                        winreg.SetValueEx(reg_key, app_name, 0, winreg.REG_SZ, app_path)
        except:
            pass

        startup_programs = []
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_READ) as reg_key:
            num_entries = winreg.QueryInfoKey(reg_key)[0]
            for i in range(num_entries):
                try:
                    app_name, app_path, _ = winreg.EnumValue(reg_key, i)
                    startup_programs.append((app_name, app_path))
                except:
                    pass

        message = "Los siguientes programas se ejecutarán al iniciar Windows. Seleccione los programas que desea deshabilitar:"
        selected_programs = []
        for app_name, app_path in startup_programs:
            reply = QMessageBox.question(None, app_name, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                selected_programs.append((app_name, app_path))

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_ALL_ACCESS) as reg_key:
            for app_name, app_path in startup_programs:
                winreg.DeleteValue(reg_key, app_name)

            for app_name, app_path in selected_programs:
                winreg.SetValueEx(reg_key, app_name, 0, winreg.REG_SZ, app_path)


class MainWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Optimización de Windows')
        self.setMinimumWidth(400)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        self.label = QLabel('Seleccione una acción para optimizar Windows:')
        self.button_registry = QPushButton('Limpiar registro')
        self.button_restore_registry = QPushButton('Restaurar registro')
        self.button_junk_files = QPushButton('Limpiar archivos basura')
        self.button_startup_programs = QPushButton('Gestionar programas de inicio')

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button_restore_registry)
        layout.addWidget(self.button_junk_files)
        layout.addWidget(self.button_startup_programs)

        self.setLayout(layout)

        self.button_registry.clicked.connect(self.clean_registry)
        self.button_restore_registry.clicked.connect(self.restore_registry)
        self.button_junk_files.clicked.connect(self.clean_junk_files)
        self.button_startup_programs.clicked.connect(self.manage_startup_programs)

    def clean_registry(self):
        # Limpiar registro
        message = "Esta acción eliminará las entradas no utilizadas del registro y podría mejorar el rendimiento del sistema. ¿Desea continuar?"
        reply = QMessageBox.question(self, 'Limpiar registro', message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                backup_path = os.path.join(os.getenv('TEMP'), 'registry_backup.reg')
                command = f'reg export HKCU\\Software {backup_path}'
                subprocess.call(command, shell=True)

                command = 'reg delete HKCU\\Software\\ /f'
                subprocess.call(command, shell=True)

                message = "El registro ha sido limpiado con éxito."
                QMessageBox.information(self, 'Registro limpiado', message)
            except:
                message = "Ha ocurrido un error al intentar limpiar el registro."
                QMessageBox.critical(self, 'Error', message)

    def restore_registry(self):
        # Restaurar registro
        message = "Esta acción restaurará una copia de seguridad del registro. ¿Desea continuar?"
        reply = QMessageBox.question(self, 'Restaurar registro', message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                backup_path = QFileDialog.getOpenFileName(self, 'Seleccionar archivo de copia de seguridad', os.getenv('TEMP'), "Archivos REG (*.reg)")[0]
                if backup_path:
                    command = f'reg import "{backup_path}"'
                    subprocess.call(command, shell=True)

                    message = "La copia de seguridad del registro ha sido restaurada con éxito."
                    QMessageBox.information(self, 'Registro restaurado', message)
            except:
                message = "Ha ocurrido un error al intentar restaurar la copia de seguridad del registro."
                QMessageBox.critical(self, 'Error', message)

    def clean_junk_files(self):
        # Limpiar archivos basura
        message = "Esta acción eliminará los archivos temporales y basura del sistema y podría mejorar el rendimiento del sistema. La Papelera de reciclaje también será vaciada. ¿Desea continuar?"
        reply = QMessageBox.question(self, 'Limpiar archivos basura', message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                # Vaciar la Papelera
                winshell.recycle_bin().empty(confirm=False, show_progress=False)

                # Eliminar archivos basura
                command = 'cleanmgr /sagerun:1'
                subprocess.call(command, shell=True)

                # Calcular espacio liberado
                space_freed = self.calculate_space_freed()

                message = f"Los archivos basura han sido eliminados con éxito. La Papelera de reciclaje también ha sido vaciada. Se ha liberado un total de {space_freed:.2f} MB."
                QMessageBox.information(self, 'Archivos basura eliminados', message)
            except:
                message = "Ha ocurrido un error al intentar eliminar los archivos basura."
                QMessageBox.critical(self, 'Error', message)


    def manage_startup_programs(self):
        # Gestionar programas de inicio
        try:
            startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
            for file_name in os.listdir(startup_folder):
                file_path = os.path.join(startup_folder, file_name)
                if file_path.endswith('.lnk'):
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_ALL_ACCESS) as reg_key:
                        app_name = file_name.split('.')[0]
                        app_path = file_path.replace('\\', '/')
                        winreg.SetValueEx(reg_key, app_name, 0, winreg.REG_SZ, app_path)
        except Exception as e:
            message = "Ha ocurrido un error al intentar gestionar los programas de inicio:\n\n{}".format(str(e))
            QMessageBox.critical(None, 'Error', message)
            pass

        startup_programs = []
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_READ) as reg_key:
            num_entries = winreg.QueryInfoKey(reg_key)[0]
            for i in range(num_entries):
                try:
                    app_name, app_path, _ = winreg.EnumValue(reg_key, i)
                    startup_programs.append((app_name, app_path))
                except:
                    pass

        message = "Los siguientes programas se ejecutarán al iniciar Windows. Seleccione los programas que desea deshabilitar:"
        selected_programs = []
        for app_name, app_path in startup_programs:
            reply = QMessageBox.question(None, app_name, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                selected_programs.append((app_name, app_path))

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_ALL_ACCESS) as reg_key:
            for app_name, app_path in startup_programs:
                winreg.DeleteValue(reg_key, app_name)

            for app_name, app_path in selected_programs:
                winreg.SetValueEx(reg_key, app_name, 0, winreg.REG_SZ, app_path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
