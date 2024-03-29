"""Контроллер главного окна модуля отвода
Содержит обработчики кликов на кнопки, хранит значение магнитного склонения,
формат данных и тип координат, значение точки привязки, 
обертку над таблицей (tablewrapper) для доступа к данным отвода
"""

import os
import json
from .MainWindow import MainWindow
from .CanvasWidget import CanvasWidget
from .ui.SwitchButton import Switch
from .gui.LesosekaInfoDialog import LesosekaInfo
from .tools import GeoOperations, ImageExporter
from .tools.tempFeatures.BindingPointBuilder import BindingPointBuilder
from . import LayoutManager
from .DataTable import DataTableWrapper
from .OtvodSettingsDialog import OtvodSettingsWindow
from ...tools import config
from .tools.mapTools.MovePointMapTool import MovePointTool
from .CuttingAreaAttributesEditor import CuttingAreaAttributesEditor
from PyQt5.QtGui import QIcon
from qgis.core import QgsProject, QgsPointXY, QgsPrintLayout
from functools import partial
from qgis.PyQt.QtWidgets import (
    QMessageBox,
    QDialog,
    QButtonGroup,
    QFileDialog,
    QTableWidgetItem,
)
from qgis.PyQt.QtWidgets import QAction
from datetime import datetime
from qgis.PyQt.QtCore import Qt
from qgis.utils import iface
from qgis.gui import QgsMapToolPan, QgsMapToolAdvancedDigitizing
from .LayerManager import LayerManager, GPSLayerManager
from .icons.initIcons import IconSet
from qgis.core import Qgis, QgsSnappingConfig, QgsTolerance
from . import geomag
from .tools.Serializer import DbSerializer
from qgis.core import edit


class OtvodController:
    def __init__(self, layerList, rct):
        self.layers = layerList
        self.rct = rct

        self.omw = MainWindow(self)

        self.tableType = self.getConfigTableType()
        self.coordType = self.getConfigCoordType()
        self.magneticInclination = 0.0

        self.bindingPoint = QgsPointXY(0, 0)
        self.cuttingArea = None
        self.tableWrapper = self.loadDataTable()

        IconSet(self.omw)

        self.omw.saveData_action.triggered.connect(
            lambda: self.saveDataToFile()
        )
        self.omw.loadData_action.triggered.connect(
            lambda: self.loadDataFromFile()
        )

        self.omw.csvExport_action.triggered.connect(lambda: self.exportToCsv())

        self.canvasWidget = CanvasWidget(
            self.omw, self.layers, self.rct, self.tableWrapper
        )

        self.omw.azimuthTool_pushButton.toggled.connect(
            partial(
                self.canvasWidget.findAzimuth, self.omw.azimuthTool_pushButton
            )
        )
        self.omw.lesoseka_from_map_button.clicked.connect(
            partial(
                self.build_from_map_clicked, self.omw.lesoseka_from_map_button
            )
        )
        self.omw.lesoseka_from_map_button.toggled.connect(
            partial(
                self.build_from_map_toggled, self.omw.lesoseka_from_map_button
            )
        )
        self.omw.lesoseka_from_map_points_button.clicked.connect(
            partial(
                self.build_from_map_clicked,
                self.omw.lesoseka_from_map_points_button,
            )
        )
        self.omw.lesoseka_from_map_points_button.toggled.connect(
            partial(
                self.build_from_map_toggled,
                self.omw.lesoseka_from_map_points_button,
            )
        )

        self.omw.saveData_pushButton.clicked.connect(
            lambda: self.saveDataToFile()
        )
        self.omw.loadData_pushButton.clicked.connect(
            lambda: self.loadDataFromFile()
        )

        self.omw.inclinationSlider.valueChanged.connect(
            self.inclinationValueChanged
        )
        self.omw.inclinationSlider.sliderMoved.connect(self.updateSliderLabel)

        self.omw.editAttributes_button.clicked.connect(self.editAreaAttributes)

        self.omw.peekFromMap_PushButton.toggled.connect(
            partial(
                self.canvasWidget.peekPointFromMap,
                self.omw.peekFromMap_PushButton,
            )
        )
        self.omw.peekVydelFromMap_pushButton.toggled.connect(
            partial(
                self.canvasWidget.peekVydelFromMap,
                self.omw.peekVydelFromMap_pushButton,
            )
        )

        self.tableWrapper.tableModel.signal.connect(
            self.canvasWidget.showPointOnCanvas
        )

        self.omw.peekFromGPSPushButton.clicked.connect(self.getGPSCoords)
        self.omw.generateReport_Button.clicked.connect(self.generateLayout)

        self.omw.buildLesoseka_Button.clicked.connect(
            self.canvasWidget.buildLesosekaFromMap
        )
        self.omw.saveLesoseka_Button.clicked.connect(self.saveCuttingArea)
        self.omw.deleteLesoseka_Button.clicked.connect(self.deleteCuttingArea)

        self.omw.x_coord_LineEdit.textChanged.connect(
            self.bindingPointCoordChanged
        )
        self.omw.y_coord_LineEdit.textChanged.connect(
            self.bindingPointCoordChanged
        )

        self.radio_group = self.setup_radio_buttons()
        self.radio_group.buttonClicked.connect(self.radio_clicked)
        self.radio_group.buttonToggled.connect(self.radio_clicked)
        # self.omw.coord_radio_button.toggle()

        self.canvas = self.canvasWidget.getCanvas()
        self.omw.show()
        self.switch = self.initSwitchButton()

        self.omw.handTool_button.clicked.connect(self.initHandTool)
        self.omw.movePoint_button.clicked.connect(self.enableMovePointTool)

        self.panTool = QgsMapToolPan(self.canvas)

        self.omw.manageLayers_button.clicked.connect(self.manageCanvasLayers)

        self.turnOnTableAndCoords()

        self.initSnapping()

        self.omw.magneticDeclination_pushButton.clicked.connect(
            self.getMagneticInclination
        )

        self.project = QgsProject.instance()
        self.imgExporter = ImageExporter.ImageExporter(
            self.project, self.canvas
        )
        self.omw.exportAsImage_PushButton.clicked.connect(self.generateImage)

        self.omw.gpsTablet_pushButton.clicked.connect(self.loadPointsFromLayer)

    def loadPointsFromLayer(self):
        self.manager = GPSLayerManager(self.canvas)
        if self.manager.initWidget():
            
            layerVd = QgsProject.instance().mapLayersByName("Выдела")[0]
            iface.setActiveLayer(layerVd)

            self.omw.coord_radio_button.toggle()
            self.canvasWidget.table.deleteRows()   

            ptList = self.manager.getPointsOfLayerAsList()
            if ptList:
                bindingPoint = GeoOperations.convertToWgs(ptList[0][0])
                self.omw.y_coord_LineEdit.setText(str(bindingPoint.x()))
                self.omw.x_coord_LineEdit.setText(str(bindingPoint.y()))
                self.canvasWidget.table.appendTableFromMap(ptList[1:] + [ptList[0]])
        
    def enableMovePointTool(self):
        layer = QgsProject.instance().mapLayersByName('Пикеты')
        if layer:
            self.mpt = MovePointTool(self.canvas, self.tableWrapper.tableModel)
            self.canvas.setMapTool(self.mpt)
        else:
            QMessageBox.information(
                None,
                "Ошибка модуля ГИСлесхоз",
                "Отсутствует слой пикетов",
            )

    def exportToCsv(self):
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y %H.%M")
        filename = QFileDialog.getSaveFileName(
            None,
            "Сохранить точки отвода",
            "Данные отвода от " + dt_string,
            "Точки отвода (*.csv)",
        )[0]
        if not filename:
            return
        else:
            with open(filename, "w", encoding="utf8") as write_file:
                data = self.tableWrapper.serializePointsToCsv()
                for line in data:
                    write_file.write(line + "\n")
            self.omw.outputLabel.setText(
                "<a href=file:///{}>Открыть папку</a>".format(
                    os.path.dirname(filename)
                )
            )
            self.omw.outputLabel.setOpenExternalLinks(True)

    def generateImage(self):
        path = self.imgExporter.doJob(self.tableWrapper.getJSONRows())
        self.omw.outputLabel.setText(
            "<a href=file:///{}>Открыть картинку</a>".format(
                os.path.realpath(path)
            )
        )
        self.omw.outputLabel.setOpenExternalLinks(True)

    def getMagneticInclination(self):
        point = GeoOperations.convertToWgs(self.canvas.center())
        declination = geomag.declination(point.y(), point.x())
        self.omw.inclinationSlider.setValue(declination * 10)

    def turnOnTableAndCoords(self):
        tableTypeButton = self.radio_group.button(self.tableType)
        tableTypeButton.toggle()
        if self.coordType:
            self.switch.setChecked(True)
        else:
            self.switch.setChecked(False)

    def getConfigTableType(self):
        cf = config.Configurer("otvod")
        settings = cf.readConfigs()
        return int(settings.get("tabletype", "No data"))

    def getConfigCoordType(self):
        cf = config.Configurer("otvod")
        settings = cf.readConfigs()
        return int(settings.get("coordtype", "No data"))

    def initSnapping(self):
        my_snap_config = QgsSnappingConfig()
        my_snap_config.setEnabled(True)
        my_snap_config.setType(QgsSnappingConfig.VertexAndSegment)
        my_snap_config.setUnits(QgsTolerance.Pixels)
        my_snap_config.setTolerance(10)
        my_snap_config.setIntersectionSnapping(True)
        my_snap_config.setMode(QgsSnappingConfig.AllLayers)
        QgsProject.instance().setSnappingConfig(my_snap_config)

    def manageCanvasLayers(self):
        self.manager = LayerManager(self.canvas)
        if self.manager.initWidget():
            self.manager.changeLayers(self.manager.checkBoxes)

    def initHandTool(self):
        self.canvas.setMapTool(self.panTool)

    def updateSliderLabel(self, value):
        self.omw.sliderLabel.setText(str(value / 10))

    def inclinationValueChanged(self, value):
        if self.tableWrapper.getRowsCount() > 0 and self.tableType != 0:
            currentMagneticInclination = (
                self.tableWrapper.getMagneticInclination()
            )
            inclinationDifference = currentMagneticInclination - value / 10
            self.tableWrapper.tableModel.setMagneticInclinationDifference(
                inclinationDifference
            )
            # self.tableWrapper.updateTableDataInclination(inclinationDifference)

        self.magneticInclination = value / 10
        self.tableWrapper.tableModel.setMagneticInclination(
            self.magneticInclination
        )

        self.tableWrapper.tableModel.refreshData()
        self.omw.sliderLabel.setText(str(self.magneticInclination))

    def initSwitchButton(self):
        s4 = Switch(thumb_radius=6, track_radius=8)
        s4.toggled.connect(partial(self.switchClicked, s4))
        self.omw.switchLayout.addWidget(s4)
        return s4

    def switchClicked(self, switch):
        if not self.tableWrapper.tableModel.ensureTableCellsNotEmpty():
            switch.blockSignals(True)
            if switch.isChecked():
                switch.setChecked(False)
            else:
                switch.setChecked(True)
            switch.blockSignals(False)
        else:
            if switch.isChecked():
                self.coordType = 1
            else:
                self.coordType = 0
            self.tableWrapper.convertCoordFormat(self.coordType)

    def editAreaAttributes(self):
        editor = CuttingAreaAttributesEditor(self.cuttingArea)
        editor.editAreaAttributes()

    def disableRadioGroup(self, bl):
        for button in self.radio_group.buttons():
            button.setEnabled(bl)

    def build_from_map_clicked(self, btn, btnState):
        self.disableRadioGroup(False)
        # self.coordType = 0
        self.switch.setChecked(False)
        self.canvasWidget.build_from_map(
            btn, btnState, self.radio_group.buttons()
        )

    def build_from_map_toggled(self, btn, btnState):
        if btnState == True:
            self.disableRadioGroup(False)
            self.deleteCuttingArea()
        else:
            self.canvasWidget.build_from_map(
                btn, btnState, self.radio_group.buttons()
            )

    def setup_radio_buttons(self):
        radio_group = QButtonGroup()  # Number group
        radio_group.addButton(self.omw.coord_radio_button)
        radio_group.addButton(self.omw.azimuth_radio_button)
        radio_group.addButton(self.omw.rumb_radio_button)
        radio_group.addButton(self.omw.left_angle_radio_button)
        radio_group.addButton(self.omw.right_angle_radio_button)
        i = 0
        for btn in radio_group.buttons():
            radio_group.setId(btn, i)
            i += 1
        return radio_group

    def radio_clicked(self, button):
        if self.tableType == self.radio_group.id(button):
            pass
        elif self.tableWrapper.tableModel.ensureTableCellsNotEmpty():
            buttonId = self.radio_group.id(button)
            currentTableType = self.tableType
            self.tableType = buttonId
            self.tableWrapper.convertCells(
                currentTableType,
                buttonId,
                self.tableType,
                self.coordType,
                float(self.tableWrapper.getMagneticInclination()),
                self.bindingPoint,
            )
        else:
            for btn in self.radio_group.buttons():
                if self.tableType == self.radio_group.id(btn):
                    btn.setChecked(True)
        if self.radio_group.id(button) == 0:
            self.omw.inclinationSlider.setEnabled(False)
            self.omw.magneticDeclination_pushButton.setEnabled(False)
        else:
            self.omw.inclinationSlider.setEnabled(True)
            self.omw.magneticDeclination_pushButton.setEnabled(True)

    def bindingPointCoordChanged(self):
        e = n = 0
        try:
            nRaw = self.omw.x_coord_LineEdit.text().replace(",", ".")
            eRaw = self.omw.y_coord_LineEdit.text().replace(",", ".")
            n = float(nRaw)
            e = float(eRaw)
        except Exception as e:
            n = 0
            e = 0
            print("Ошибка формата точки привязки")
            # QMessageBox.information(None, "Ошибка данных точки привязки", str(e))

        if 50.0 <= n <= 57.0 and 20.0 <= e <= 33.0:
            self.bindingPoint = GeoOperations.convertToZone35(QgsPointXY(e, n))
            bp = BindingPointBuilder(self.bindingPoint, self.canvas)
            bp.makeFeature()
            self.tableWrapper.tableModel.setBindingPointXY(self.bindingPoint)
            self.tableWrapper.tableModel.refreshData()

    def getGPSCoords(self):
        gpsCoords = GeoOperations.getCoordFromGPS()
        if gpsCoords:
            self.omw.y_coord_LineEdit.setText(str(round(gpsCoords[0], 10)))
            self.omw.x_coord_LineEdit.setText(str(round(gpsCoords[1], 10)))

    def loadDataTable(self):
        datatable = DataTableWrapper(
            self.omw.verticalLayout_6,
            int(self.tableType),
            int(self.coordType),
            0,
            self.bindingPoint,
            self.omw.inclinationSlider,
        )
        datatable.deleteRows()
        self.omw.addNode_button.clicked.connect(datatable.addRow)
        self.omw.deleteNode_button.clicked.connect(datatable.deleteRow)
        self.omw.clearNodes_button.clicked.connect(
            partial(self.clearNodes, datatable)
        )

        return datatable

    def clearNodes(self, datatable):
        datatable.deleteRows()
        self.deleteCuttingArea()

    def parseConfig(self):
        cf = config.Configurer("otvod")
        moduleSettings = cf.readConfigs()
        return [
            moduleSettings.get("tabletype", "No data"),
            moduleSettings.get("coordtype", "No data"),
        ]

    def otvodMenuSettings(self):
        self.sw = OtvodSettingsWindow()
        self.ui = self.sw.ui
        self.ui.tabletype_comboBox.setCurrentIndex(int(self.tableType))
        self.ui.coordtype_comboBox.setCurrentIndex(int(self.coordType))
        self.ui.magnIncl_lineEdit.setText(str(self.magneticInclination))
        dialogResult = self.sw.exec()
        if dialogResult == QDialog.Accepted:
            tableType = int(
                self.sw.tabletypes.get(
                    self.ui.tabletype_comboBox.currentText()
                )
            )
            coordType = int(
                self.sw.coordtypes.get(
                    self.ui.coordtype_comboBox.currentText()
                )
            )
            magneticInclination = self.ui.magnIncl_lineEdit.text()
            if (
                self.tableType == tableType
                and self.coordType == coordType
                and self.magneticInclination == magneticInclination
            ):
                return 0
            else:
                self.tableType = tableType
                self.coordType = coordType
                self.magneticInclination = magneticInclination
                if self.magneticInclination == "":
                    self.magneticInclination = 0
                self.tableWrapper.deleteRows()
                self.tableWrapper.tableModel.setParams(
                    self.tableType,
                    self.coordType,
                    float(self.magneticInclination),
                    self.bindingPoint,
                )

    def saveDataToFile(self):
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y %H.%M")
        filename = QFileDialog.getSaveFileName(
            None,
            "Сохранить файл отвода",
            "Данные отвода от " + dt_string,
            "Файлы отвода (*.json)",
        )[0]
        if not filename:
            return
        else:
            with open(filename, "w", encoding="utf8") as write_file:
                json.dump(
                    self.tableWrapper,
                    write_file,
                    default=self.tableWrapper.encodeJSON,
                    ensure_ascii=False,
                    indent=4,
                )
            self.omw.outputLabel.setText(
                "<a href=file:///{}>Открыть папку</a>".format(
                    os.path.dirname(filename)
                )
            )
            self.omw.outputLabel.setOpenExternalLinks(True)

    def loadDataFromFile(self):
        try:
            self.tableWrapper.tableModel.setRerender(False)
            table = self.tableWrapper.tableModel
            filename = QFileDialog.getOpenFileName(
                None, "Открыть файл отвода", "", "Файлы отвода (*.json)"
            )[0]
            if not filename:
                return
            else:
                with open(filename, "r", encoding="utf8") as read_file:
                    data = json.load(read_file)
            if data:
                self.deleteCuttingArea()
                for p in data:
                    for key, value in p.items():
                        if key == "Table":
                            self.tableType = data[0]["Table"]["table_type"]
                            btn = self.radio_group.button(self.tableType)
                            btn.setChecked(True)
                            self.coordType = data[0]["Table"]["coord_type"]
                            if self.coordType == 0:
                                self.switch.setChecked(False)
                            if self.coordType == 1:
                                self.switch.setChecked(True)
                            self.magneticInclination = data[0]["Table"][
                                "magnetic_inclination"
                            ]
                            self.omw.inclinationSlider.setValue(
                                self.magneticInclination * 10
                            )
                            self.omw.sliderLabel.setText(
                                str(self.magneticInclination)
                            )
                            point35 = QgsPointXY(
                                float(data[0]["Table"]["BindingPointX"]),
                                float(data[0]["Table"]["BindingPointY"]),
                            )
                            point = GeoOperations.convertToWgs(point35)
                            self.omw.y_coord_LineEdit.setText(str(point.x()))
                            self.omw.x_coord_LineEdit.setText(str(point.y()))
                            self.canvas.setCenter(point35)
                            self.tableWrapper.deleteRows()
                            self.tableWrapper.tableModel.setParams(
                                self.tableType,
                                self.coordType,
                                self.magneticInclination,
                                self.bindingPoint,
                            )
                            continue
                        else:
                            self.tableWrapper.addRow()
                            i = 0
                            for k, v in value.items():
                                if (
                                    table.horizontalHeaderItem(i).text()
                                    == "Румб"
                                    or table.horizontalHeaderItem(i).text()
                                    == "Тип"
                                ):
                                    comboboxCellWidget = table.cellWidget(
                                        int(key), int(i)
                                    )
                                    index = comboboxCellWidget.findText(
                                        str(v), Qt.MatchFixedString
                                    )
                                    if index >= 0:
                                        comboboxCellWidget.setCurrentIndex(
                                            index
                                        )
                                item = QTableWidgetItem()
                                item.setText(str(v))
                                table.setItem(int(key), int(i), item)
                                i = i + 1
        except Exception as e:
            print(e)
        finally:
            self.tableWrapper.tableModel.setRerender(True)
            self.tableWrapper.tableModel.refreshData()

    def saveCuttingArea(self):
        def getEditedUid():
            layer = QgsProject.instance().mapLayersByName(
                "Лесосека временный слой"
            )
            if layer:
                feature = list(layer[0].getFeatures())[0]
                return feature["uid"]
            return None

        def saveDataToDatabase():
            tableData = self.tableWrapper.getSerializableData()
            data = [uid] + tableData
            DbSerializer(data).saveToDb()

        def copyFromTempLayer(sourceLYRName, destLYRName):
            sourceLYR = QgsProject.instance().mapLayersByName(sourceLYRName)[0]
            destLYR = QgsProject.instance().mapLayersByName(destLYRName)[0]

            features = destLYR.getFeatures("uid = '{}'".format(uid))

            if destLYR.isEditable():
                iface.setActiveLayer(destLYR)
                iface.mainWindow().findChild(
                    QAction, "mActionToggleEditing"
                ).trigger()

            with edit(destLYR):
                for f in features:
                    destLYR.deleteFeature(f.id())

            features = []
            for feature in sourceLYR.getFeatures():
                features.append(feature)
            destLYR.startEditing()
            data_provider = destLYR.dataProvider()
            data_provider.addFeatures(features)
            destLYR.commitChanges()

        uid = getEditedUid()

        layer = QgsProject.instance().mapLayersByName("Результат обрезки")
        if layer:
            QgsProject.instance().removeMapLayers([layer[0].id()])

        self.canvas.refreshAllLayers()

        layer = QgsProject.instance().mapLayersByName(
            "Лесосека временный слой"
        )
        if not layer:
            QMessageBox.information(
                None,
                "Ошибка модуля ГИСлесхоз",
                "Отсутствует лесосека. Постройте лесосеку, после чего будет возможность ее сохранить",
            )

        layer = QgsProject.instance().mapLayersByName(
            "Привязка временный слой"
        )
        if layer:
            copyFromTempLayer("Привязка временный слой", "Линия привязки")
            copyFromTempLayer("Лесосека временный слой", "Лесосеки")
        else:
            copyFromTempLayer("Лесосека временный слой", "Лесосеки")

        saveDataToDatabase()

        self.canvasWidget.btnControl.unlockReportBotton()
        self.omw.outputLabel.setText("Лесосека сохранена")

    def deleteCuttingArea(self):
        layerNamesToDelete = [
            "Точка привязки",
            "Лесосека временный слой",
            "Опорные точки",
            "Привязка временный слой",
            "Пикеты",
            "Результат обрезки",
        ]

        for name in layerNamesToDelete:
            layer = QgsProject.instance().mapLayersByName(name)
            if layer:
                QgsProject.instance().removeMapLayers([layer[0].id()])

        self.magneticInclination = 0.0
        self.canvasWidget.btnControl.lockLesosekaButtons()
        self.tableWrapper.deleteRows()
        self.omw.y_coord_LineEdit.clear()
        self.omw.x_coord_LineEdit.clear()
        self.canvas.refresh()
        iface.mapCanvas().refresh()

    def generateLayout(self):
        layout = LayoutManager.LayoutManager(
            self.canvas, self.bindingPoint, self.tableType, self.coordType
        )
        layout.generate(
            [self.tableWrapper.getColumnNames()]
            + self.tableWrapper.copyTableData()
        )
