"""
Настройки модуля хранятся в файле config.ini


Настройки: 
- Доступ к базе данных
- Подключение к видке и дальномеру (устарело) по Bluetooth
- Предпочитаемый формат отвода (автоматически устанавливается в окно отвода)
- Данные об учреждении (нужны для формирования отчета):
    - Местоположение, тип, ведомство и тп
    - Номер лесхоза и код лесхоза - нужны для сохранения и загрузки данных из БД
- Путь к отчету Word (устарело)
"""

from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QToolButton, QFileDialog
from .gui import settingsDialog, changePortDialog
from .tools import config
from .tools.ImportDatabase import DataImport
from .tools.SqlFileExecuter import SqlFileExecuter
from .tools import module_errors as er
from .PostgisDB import PostGisDB
from PyQt5 import QtCore
from .modules.otvod.tools.threading.ForestObjectWorker import (
    Worker as ForestObjWorker,
)
from .modules.otvod.tools.threading.ForestObjectLoader import (
    ForestObjectLoader,
)
from qgis.utils import iface
import os
from .modules.trees_accounting.src.services.waiting_spinner_widget import (
    QtWaitingSpinner,
)


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.ui = settingsDialog.Ui_settingsDialog()
        self.ui.setupUi(self)


class comPortWindow(QDialog):
    def __init__(self, parent=None):
        super(comPortWindow, self).__init__(parent)
        self.ui = changePortDialog.Ui_Dialog()
        self.ui.setupUi(self)


class SettingsController(QtCore.QObject):
    """Контроллер окна настроек
    """
    def __init__(self, *args, **kwargs):
        QtCore.QObject.__init__(self)
        self.sd = SettingsWindow()
        self.sd.setModal(False)
        self.tableUi = self.sd.ui

        self.spinner = QtWaitingSpinner(
            self.sd, True, True, QtCore.Qt.ApplicationModal
        )

        self.tabletypes = {
            "Координаты": 0,
            "Азимуты": 1,
            "Румбы": 2,
            "Левые углы": 3,
            "Правые углы": 4,
        }
        self.coordtypes = {"Десятичный": 0, "Градусы/Минуты/Секунды": 1}

        self.populateOtvodSettings()

        (
            self.location,
            self.num_lhz,
            self.gplho,
            self.lh_type,
            self.leshoz,
            self.lesnich,
        ) = self.getEnterpriseConfig()

        self.populateLocation(self.location)

        self.populateEnterprise()

        self.populateBDSettings()

        self.tableUi.saveConfigButton.clicked.connect(self.saveBDConfig)
        self.tableUi.importDB_pushButton.clicked.connect(self.importDB)
        self.tableUi.testDBConnection_pushButton.clicked.connect(
            self.getDBConnectionState
        )
        self.tableUi.saveEnterpriseSettingsButton.clicked.connect(
            self.saveEnterpriseConfig
        )

        self.tableUi.gplho_comboBox.currentTextChanged.connect(
            self.gplhoChanged
        )
        self.tableUi.leshoz_comboBox.currentTextChanged.connect(
            self.leshozChanged
        )

        self.tableUi.toolButton.clicked.connect(self.chooseReportFolder)
        self.tableUi.saveOtvodSettingsButton.clicked.connect(
            self.saveOtvodSettings
        )
        self.tableUi.run_sql_pushButton.clicked.connect(self.runSqlScript)
        self.sd.exec()

        self.lhTypesAndNames = None

    def populateLocation(self, location):
        self.tableUi.locationLineEdit.setText(location)

    def getEnterpriseConfig(self):
        cf = config.Configurer("enterprise")
        settings = cf.readConfigs()
        return [
            settings.get("location", ""),
            settings.get("num_lhz", ""),
            settings.get("gplho", ""),
            settings.get("type", ""),
            settings.get("leshoz", ""),
            settings.get("lesnich", ""),
        ]

    def saveEnterpriseConfig(self):
        try:
            leshoz = self.tableUi.leshoz_comboBox.currentText()
            lhType = self.lhTypesAndNames.get(leshoz, "")
            settingsDict = {
                "location": self.tableUi.locationLineEdit.text(),
                "num_lhz": self.num_lhz,
                "gplho": self.tableUi.gplho_comboBox.currentText(),
                "type": lhType,
                "leshoz": leshoz,
                "lesnich": self.tableUi.lesnich_comboBox.currentText(),
            }
            cf = config.Configurer("enterprise", settingsDict)
            cf.writeConfigs()
        except Exception as e:
            QMessageBox.information(
                None, er.MODULE_ERROR, er.CONFIG_FILE_ERROR + str(e)
            )

    def gplhoChanged(self):
        if self.tableUi.gplho_comboBox.currentText() == "":
            return

        def workerFinished(result):
            worker.deleteLater()
            thread.quit()
            thread.wait()
            thread.deleteLater()

            self.comboboxClear(
                self.tableUi.leshoz_comboBox, self.tableUi.lesnich_comboBox
            )
            self.clearComboboxIndex(
                self.tableUi.leshoz_comboBox, self.tableUi.lesnich_comboBox
            )
            self.tableUi.leshoz_comboBox.addItem("")
            self.tableUi.leshoz_comboBox.addItems(result[1].values())
            self.lhTypesAndNames = result[4]
            if self.leshoz:
                index = self.tableUi.leshoz_comboBox.findText(self.leshoz)
                if index >= 0:
                    self.tableUi.leshoz_comboBox.setCurrentIndex(index)

        thread = QtCore.QThread(iface.mainWindow())
        worker = ForestObjWorker()
        worker.moveToThread(thread)
        worker.finished.connect(workerFinished)
        worker.gplho = self.tableUi.gplho_comboBox.currentText()
        worker.leshoz = None
        thread.started.connect(worker.run)
        thread.start()

    def leshozChanged(self):

        if self.tableUi.leshoz_comboBox.currentText() == "":
            return

        def workerFinished(result):
            worker.deleteLater()
            thread.quit()
            thread.wait()
            thread.deleteLater()
            self.comboboxClear(self.tableUi.lesnich_comboBox)
            self.clearComboboxIndex(self.tableUi.lesnich_comboBox)

            self.tableUi.lesnich_comboBox.addItems(result[2].values())
            if self.lesnich:
                index = self.tableUi.lesnich_comboBox.findText(self.lesnich)
                if index >= 0:
                    self.tableUi.lesnich_comboBox.setCurrentIndex(index)

        thread = QtCore.QThread(iface.mainWindow())
        worker = ForestObjWorker()
        worker.moveToThread(thread)
        worker.finished.connect(workerFinished)
        worker.gplho = self.tableUi.gplho_comboBox.currentText()
        worker.leshoz = self.tableUi.leshoz_comboBox.currentText()
        thread.started.connect(worker.run)
        thread.start()

    def populateEnterprise(self):
        def workerFinished(result):
            worker.deleteLater()
            thread.quit()
            thread.wait()
            thread.deleteLater()
            self.tableUi.gplho_comboBox.addItem("")
            self.tableUi.gplho_comboBox.addItems(result[0].values())

            if self.gplho:
                index = self.tableUi.gplho_comboBox.findText(self.gplho)
                if index >= 0:
                    self.tableUi.gplho_comboBox.setCurrentIndex(index)

        thread = QtCore.QThread(iface.mainWindow())
        worker = ForestObjWorker()
        worker.moveToThread(thread)
        worker.finished.connect(workerFinished)
        thread.started.connect(worker.run)
        thread.start()

    def comboboxClear(self, *args):
        for arg in args:
            arg.clear()

    def clearComboboxIndex(self, *args):
        for arg in args:
            arg.setCurrentIndex(-1)

    def saveOtvodSettings(self):
        cfReport = config.Configurer(
            "report", {"path": self.tableUi.lineEdit.text()}
        )
        cfReport.writeConfigs()
        otvodSettings = {
            "tabletype": str(
                self.tabletypes.get(
                    self.tableUi.tableType_comboBox.currentText(), "0"
                )
            ),
            "coordtype": str(
                self.coordtypes.get(
                    self.tableUi.coordType_comboBox.currentText(), "0"
                )
            ),
        }
        cfOtvod = config.Configurer("otvod", otvodSettings)
        cfOtvod.writeConfigs()

    def chooseReportFolder(self):
        cfReport = config.Configurer("report")
        settingsReport = cfReport.readConfigs()
        oldPath = settingsReport.get("path", "")
        path = str(QFileDialog.getExistingDirectory(None, "Select Directory"))
        if not path and oldPath:
            path = oldPath
        if not path and not oldPath:
            path = os.path.expanduser("~")
        self.tableUi.lineEdit.setText(path)

    def populateOtvodSettings(self):
        self.tableUi.tableType_comboBox.addItems(
            [key for key, value in self.tabletypes.items()]
        )
        self.tableUi.coordType_comboBox.addItems(
            [key for key, value in self.coordtypes.items()]
        )
        cfReport = config.Configurer("report")
        cfOtvod = config.Configurer("otvod")
        settingsReport = cfReport.readConfigs()
        self.tableUi.lineEdit.setText(settingsReport.get("path", "No data"))
        settingsOtvod = cfOtvod.readConfigs()
        self.tableUi.tableType_comboBox.setCurrentIndex(
            int(settingsOtvod.get("tabletype"))
        )
        self.tableUi.coordType_comboBox.setCurrentIndex(
            int(settingsOtvod.get("coordtype"))
        )

    def populateBDSettings(self):
        try:
            cf = config.Configurer("dbconnection")
            bdsettings = cf.readConfigs()
            self.tableUi.connectionLineEdit.setText(
                bdsettings.get("host", "No data")
            )
            self.tableUi.portLineEdit.setText(
                bdsettings.get("port", "No data")
            )
            self.tableUi.usernameLineEdit.setText(
                bdsettings.get("user", "No data")
            )
            self.tableUi.passwordLineEdit.setText(
                bdsettings.get("password", "No data")
            )
            self.tableUi.BDNameLineEdit.setText(
                bdsettings.get("database", "No data")
            )
        except Exception as e:
            QMessageBox.information(
                None, er.MODULE_ERROR, er.CONFIG_FILE_ERROR + str(e)
            )

    def saveBDConfig(self):
        try:
            settingsDict = {
                "host": self.tableUi.connectionLineEdit.text(),
                "port": self.tableUi.portLineEdit.text(),
                "user": self.tableUi.usernameLineEdit.text(),
                "password": self.tableUi.passwordLineEdit.text(),
                "database": self.tableUi.BDNameLineEdit.text(),
            }
            cf = config.Configurer("dbconnection", settingsDict)
            cf.writeConfigs()

        except Exception as e:
            QMessageBox.information(
                None, er.MODULE_ERROR, er.CONFIG_FILE_ERROR + str(e)
            )

    def getDBConnectionState(self):
        dbconnection = PostGisDB()
        tc = dbconnection.testConnection(
            host=self.tableUi.connectionLineEdit.text(),
            port=self.tableUi.portLineEdit.text(),
            user=self.tableUi.usernameLineEdit.text(),
            password=self.tableUi.passwordLineEdit.text(),
            database=self.tableUi.BDNameLineEdit.text(),
        )
        if tc:
            QMessageBox.information(
                None, er.MODULE_ERROR, er.CONNECTION_SUCCEEDED
            )
        else:
            QMessageBox.information(
                None, er.MODULE_ERROR, er.DATABASE_CONNECTION_ERROR
            )

    def importDB(self):
        """
        Импорт базы данных  из файла.
        Перед импортом проверяется соединение с СУБД.
        """

        dbconnection = PostGisDB()
        tc = dbconnection.testConnection(
            host=self.tableUi.connectionLineEdit.text(),
            port=self.tableUi.portLineEdit.text(),
            user=self.tableUi.usernameLineEdit.text(),
            password=self.tableUi.passwordLineEdit.text(),
            database=None,
        )
        if not tc:
            QMessageBox.information(
                None, er.MODULE_ERROR, er.DBMS_CONNECTION_ERROR
            )
            return False

        result = QMessageBox.question(
            None,
            "",
            "Данные базы данных будут ПЕРЕЗАПИСАНЫ. Продолжить?",
            QMessageBox.StandardButtons(QMessageBox.Yes | QMessageBox.No),
        )
        if result == QMessageBox.Yes:
            bu_file = QFileDialog.getOpenFileName(None, "Выбор файла")[0]

            if bu_file != "":
                db_info = {
                    "host": self.tableUi.connectionLineEdit.text(),
                    "port": self.tableUi.portLineEdit.text(),
                    "user": self.tableUi.usernameLineEdit.text(),
                    "password": self.tableUi.passwordLineEdit.text(),
                    "database": self.tableUi.BDNameLineEdit.text(),
                }

                self.imported_data = DataImport(
                    db_info=db_info, filename=bu_file
                )
                self.imported_data.started.connect(
                    lambda: self.spinner.start()
                )
                self.imported_data.finished.connect(
                    lambda: self.spinner.stop()
                )
                self.imported_data.start()
                self.imported_data.signal_message_result.connect(
                    lambda mes: QMessageBox.information(None, "", str(mes)),
                    QtCore.Qt.QueuedConnection,
                )

            else:
                return False

    def runSqlScript(self):
        """
        Выполнение выбранного SQL скрипта
        """

        sql_path_file = QFileDialog.getOpenFileName(None, "Выбор файла")[0]

        if sql_path_file != "":

            self.sql_file_executer = SqlFileExecuter(
                sql_file_path=sql_path_file
            )
            self.sql_file_executer.started.connect(
                lambda: self.spinner.start()
            )
            self.sql_file_executer.finished.connect(
                lambda: self.spinner.stop()
            )
            self.sql_file_executer.start()
            self.sql_file_executer.signal_message_result.connect(
                lambda mes: QMessageBox.information(None, "", str(mes)),
                QtCore.Qt.QueuedConnection,
            )

        else:
            return False
