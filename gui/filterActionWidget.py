# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\OSGeo4W64\apps\qgis\python\plugins\QgsLes\ui\filterActionWidget.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(269, 180)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.leshoz_label_3 = QtWidgets.QLabel(Form)
        self.leshoz_label_3.setEnabled(True)
        self.leshoz_label_3.setMaximumSize(QtCore.QSize(70, 30))
        self.leshoz_label_3.setObjectName("leshoz_label_3")
        self.horizontalLayout_15.addWidget(self.leshoz_label_3)
        self.leshoz_combobox_3 = QtWidgets.QComboBox(Form)
        self.leshoz_combobox_3.setEditable(True)
        self.leshoz_combobox_3.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.leshoz_combobox_3.setObjectName("leshoz_combobox_3")
        self.horizontalLayout_15.addWidget(self.leshoz_combobox_3)
        self.verticalLayout.addLayout(self.horizontalLayout_15)
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.lch_label_3 = QtWidgets.QLabel(Form)
        self.lch_label_3.setMaximumSize(QtCore.QSize(70, 16777215))
        self.lch_label_3.setObjectName("lch_label_3")
        self.horizontalLayout_16.addWidget(self.lch_label_3)
        self.lch_combobox_3 = QtWidgets.QComboBox(Form)
        self.lch_combobox_3.setEditable(True)
        self.lch_combobox_3.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.lch_combobox_3.setObjectName("lch_combobox_3")
        self.horizontalLayout_16.addWidget(self.lch_combobox_3)
        self.verticalLayout.addLayout(self.horizontalLayout_16)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.kv_label_3 = QtWidgets.QLabel(Form)
        self.kv_label_3.setMaximumSize(QtCore.QSize(70, 16777215))
        self.kv_label_3.setObjectName("kv_label_3")
        self.horizontalLayout_12.addWidget(self.kv_label_3)
        self.kv_combobox_3 = QtWidgets.QComboBox(Form)
        self.kv_combobox_3.setEditable(True)
        self.kv_combobox_3.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.kv_combobox_3.setObjectName("kv_combobox_3")
        self.horizontalLayout_12.addWidget(self.kv_combobox_3)
        self.verticalLayout.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.vd_label_3 = QtWidgets.QLabel(Form)
        self.vd_label_3.setMaximumSize(QtCore.QSize(70, 16777215))
        self.vd_label_3.setObjectName("vd_label_3")
        self.horizontalLayout_14.addWidget(self.vd_label_3)
        self.vd_combobox_3 = QtWidgets.QComboBox(Form)
        self.vd_combobox_3.setEditable(True)
        self.vd_combobox_3.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.vd_combobox_3.setObjectName("vd_combobox_3")
        self.horizontalLayout_14.addWidget(self.vd_combobox_3)
        self.verticalLayout.addLayout(self.horizontalLayout_14)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        spacerItem = QtWidgets.QSpacerItem(75, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem)
        self.zoomTo_PushButton_3 = QtWidgets.QPushButton(Form)
        self.zoomTo_PushButton_3.setMinimumSize(QtCore.QSize(64, 0))
        self.zoomTo_PushButton_3.setObjectName("zoomTo_PushButton_3")
        self.horizontalLayout_13.addWidget(self.zoomTo_PushButton_3)
        self.clearFilter_pushButton_3 = QtWidgets.QPushButton(Form)
        self.clearFilter_pushButton_3.setObjectName("clearFilter_pushButton_3")
        self.horizontalLayout_13.addWidget(self.clearFilter_pushButton_3)
        self.verticalLayout.addLayout(self.horizontalLayout_13)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.leshoz_label_3.setText(_translate("Form", "Лесхоз"))
        self.lch_label_3.setText(_translate("Form", "Лесничество"))
        self.kv_label_3.setText(_translate("Form", "Квартал"))
        self.vd_label_3.setText(_translate("Form", "Выдел"))
        self.zoomTo_PushButton_3.setText(_translate("Form", "Найти"))
        self.clearFilter_pushButton_3.setText(_translate("Form", "Очистить фильтр"))


