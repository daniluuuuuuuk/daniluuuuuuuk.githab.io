# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\NLK\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\trial_area\modules\otvod\ui\lesosekaInfo.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(311, 509)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(140, 460, 161, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(10, 280, 91, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(10, 310, 47, 13))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(10, 380, 91, 16))
        self.label_6.setObjectName("label_6")
        self.fio = QtWidgets.QLineEdit(Dialog)
        self.fio.setGeometry(QtCore.QRect(110, 280, 191, 20))
        self.fio.setObjectName("fio")
        self.info = QtWidgets.QTextEdit(Dialog)
        self.info.setGeometry(QtCore.QRect(110, 380, 191, 71))
        self.info.setObjectName("info")
        self.num = QtWidgets.QLineEdit(Dialog)
        self.num.setGeometry(QtCore.QRect(110, 190, 191, 20))
        self.num.setObjectName("num")
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setGeometry(QtCore.QRect(10, 190, 91, 16))
        self.label_7.setObjectName("label_7")
        self.date = QtWidgets.QDateEdit(Dialog)
        self.date.setGeometry(QtCore.QRect(110, 310, 191, 22))
        self.date.setObjectName("date")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 43, 91, 16))
        self.label.setObjectName("label")
        self.label_8 = QtWidgets.QLabel(Dialog)
        self.label_8.setGeometry(QtCore.QRect(10, 70, 71, 16))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(Dialog)
        self.label_9.setGeometry(QtCore.QRect(10, 102, 47, 13))
        self.label_9.setObjectName("label_9")
        self.num_kv = QtWidgets.QLineEdit(Dialog)
        self.num_kv.setGeometry(QtCore.QRect(110, 100, 191, 20))
        self.num_kv.setObjectName("num_kv")
        self.label_10 = QtWidgets.QLabel(Dialog)
        self.label_10.setGeometry(QtCore.QRect(10, 130, 81, 16))
        self.label_10.setObjectName("label_10")
        self.num_vds = QtWidgets.QLineEdit(Dialog)
        self.num_vds.setGeometry(QtCore.QRect(110, 130, 191, 20))
        self.num_vds.setObjectName("num_vds")
        self.lesnich = QtWidgets.QComboBox(Dialog)
        self.lesnich.setGeometry(QtCore.QRect(110, 70, 191, 22))
        self.lesnich.setEditable(False)
        self.lesnich.setObjectName("lesnich")
        self.leshos = QtWidgets.QComboBox(Dialog)
        self.leshos.setGeometry(QtCore.QRect(110, 40, 191, 22))
        self.leshos.setObjectName("leshos")
        self.gplho = QtWidgets.QComboBox(Dialog)
        self.gplho.setGeometry(QtCore.QRect(110, 10, 191, 22))
        self.gplho.setObjectName("gplho")
        self.gplhoLabel = QtWidgets.QLabel(Dialog)
        self.gplhoLabel.setGeometry(QtCore.QRect(10, 14, 101, 16))
        self.gplhoLabel.setObjectName("gplhoLabel")
        self.label_11 = QtWidgets.QLabel(Dialog)
        self.label_11.setGeometry(QtCore.QRect(10, 344, 47, 13))
        self.label_11.setObjectName("label_11")
        self.restatement_comboBox = QtWidgets.QComboBox(Dialog)
        self.restatement_comboBox.setGeometry(QtCore.QRect(110, 345, 191, 22))
        self.restatement_comboBox.setObjectName("restatement_comboBox")
        self.label_12 = QtWidgets.QLabel(Dialog)
        self.label_12.setGeometry(QtCore.QRect(10, 220, 91, 16))
        self.label_12.setObjectName("label_12")
        self.label_13 = QtWidgets.QLabel(Dialog)
        self.label_13.setGeometry(QtCore.QRect(10, 250, 91, 16))
        self.label_13.setObjectName("label_13")
        self.useType = QtWidgets.QComboBox(Dialog)
        self.useType.setGeometry(QtCore.QRect(110, 220, 191, 22))
        self.useType.setObjectName("useType")
        self.cuttingType = QtWidgets.QComboBox(Dialog)
        self.cuttingType.setGeometry(QtCore.QRect(110, 250, 191, 22))
        self.cuttingType.setObjectName("cuttingType")
        self.label_14 = QtWidgets.QLabel(Dialog)
        self.label_14.setGeometry(QtCore.QRect(10, 155, 51, 16))
        self.label_14.setObjectName("label_14")
        self.area = QtWidgets.QLineEdit(Dialog)
        self.area.setGeometry(QtCore.QRect(110, 160, 191, 20))
        self.area.setReadOnly(True)
        self.area.setObjectName("area")
        self.label_15 = QtWidgets.QLabel(Dialog)
        self.label_15.setGeometry(QtCore.QRect(10, 168, 81, 16))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Данные лесосеки"))
        self.label_4.setText(_translate("Dialog", "Исполнитель"))
        self.label_5.setText(_translate("Dialog", "Дата"))
        self.label_6.setText(_translate("Dialog", "Дополнительно"))
        self.label_7.setText(_translate("Dialog", "Номер лесосеки"))
        self.label.setText(_translate("Dialog", "Учреждение"))
        self.label_8.setText(_translate("Dialog", "Лесничество"))
        self.label_9.setText(_translate("Dialog", "Квартал"))
        self.label_10.setText(_translate("Dialog", "Выдел (а)"))
        self.gplhoLabel.setText(_translate("Dialog", "ГПЛХО/ Ведомство"))
        self.label_11.setText(_translate("Dialog", "Перечет"))
        self.label_12.setText(_translate("Dialog", "Пользование"))
        self.label_13.setText(_translate("Dialog", "Вид рубки"))
        self.label_14.setText(_translate("Dialog", "Площадь"))
        self.label_15.setText(_translate("Dialog", "до увязки"))

