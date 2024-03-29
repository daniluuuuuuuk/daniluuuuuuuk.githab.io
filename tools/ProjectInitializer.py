from . import config
from qgis.core import QgsProject, QgsRasterLayer
from qgis.PyQt.QtWidgets import QMessageBox, QDialog
from qgis.core import QgsApplication, QgsCoordinateReferenceSystem, QgsVectorLayer, QgsDataSourceUri, QgsTask, QgsMessageLog, Qgis
from qgis.PyQt.QtXml import QDomDocument


class QgsProjectInitializer:
    """Класс используется для загрузки и добавления картографический слоев из БД в проект QGIS.
    К слоям применяются соответстующие стили из таблицы public.layer_styles
    Инициализируется при нажатии на кноку "Инициализировать проект"
    """
    def __init__(self, iface, qgsLesToolbar):
        super().__init__()
        if self.clearCurrentProject() == False:
            return
        self.deleteFilterWidget(qgsLesToolbar)
        self.iface = iface
        self.setCrs()
        self.settings = None
        self.layerDbNames = {'subcompartments': 'Выдела', 'hidroline': 'Гидрография линейная', 'hidropoly': 'Гидрография площадная', 'compartments': 'Кварталы',
                             'area': 'Лесосеки', 'settlements': 'Населенные пункты', 'area_line': 'Линия привязки', 'roads': 'Дороги', 
                             'forestry_borders': 'Границы лесничеств'}
        self.layerStyleNames = {'subcompartments': 'Vydela', 'hidroline': 'Hidroline', 'hidropoly': 'Hidropoly', 'compartments': 'Kvartaly',
                             'area': 'Lesoseki', 'settlements': 'Nas punkt', 'area_line': 'Privyazka', 'roads': 'Roads',
                             'forestry_borders': 'Granitsy lesnich'}
        try:
            self.cf = config.Configurer('dbconnection')
            self.settings = self.cf.readConfigs()
        except Exception as e:
            QMessageBox.information(
                None, 'Ошибка', "Проверьте подключение к базе данных" + e)
        if self.settings != None:
            self.loadLayersFromDb()

    def deleteFilterWidget(self, qgsLesToolbar):
        for action in qgsLesToolbar.actions():
            if not action.text():
                qgsLesToolbar.removeAction(action)


    def taskFinished(self):
        pass

    def clearCurrentProject(self):
        reply = QMessageBox.question(QDialog(), 'Инициализация проекта',
                                     'Слои текущего проекта будут удалены. Продолжить?', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for lyr in QgsProject.instance().mapLayers().values():
                QgsProject.instance().removeMapLayers([lyr.id()])
        else:
            return False

    def setCrs(self):
        QgsProject.instance().setCrs(QgsCoordinateReferenceSystem(32635))

    def loadLayersFromDb(self):
        self.loadTask = LoadLayersFromDbTask(self.settings, self.layerDbNames, self.layerStyleNames, self.iface)
        QgsApplication.taskManager().addTask(self.loadTask)


class LoadLayersFromDbTask(QgsTask):

    def __init__(self, settings, layerDbNames, layerStyleNames, iface):
        super().__init__("Layers from db", QgsTask.CanCancel)
        self.iface = iface
        self.settings = settings
        self.layerDbNames = layerDbNames
        self.layerStyleNames = layerStyleNames
        self.layers = []

    def run(self):
        QgsMessageLog.logMessage('Started task')
        user = self.settings.get('user')
        password = self.settings.get('password')
        host = self.settings.get('host')
        port = self.settings.get('port')
        database = self.settings.get('database')

        uri = QgsDataSourceUri()
        uri.setConnection(host, port, database, user, password)

        for tablename in self.layerDbNames:
            geom = 'geom'
            uri.setDataSource("public", tablename, geom)
            vlayer = QgsVectorLayer(
                uri.uri(False), self.layerDbNames[tablename], "postgres")
            self.layers.append(vlayer)
        return True

    def setLayerStyle(self, vlayer, tablename):
        styles = vlayer.listStylesInDatabase()
        styledoc = QDomDocument()
        styleIndex = styles[2].index(self.layerStyleNames[tablename])
        styleTuple = vlayer.getStyleFromDatabase(str(styles[1][styleIndex]))
        styleqml = styleTuple[0]
        styledoc.setContent(styleqml)
        vlayer.importNamedStyle(styledoc)
        self.iface.layerTreeView().refreshLayerSymbology(vlayer.id())

    def checkIfDatabaseIsActual(self):
        for tablename in self.layerDbNames:
            if tablename == 'agricultural_lands':
                return True

    def loadSatelliteImage(self):
        urlWithParams = 'type=xyz&zmin=10&zmax=19&url=https://mt1.google.com/vt/lyrs%3Ds%26x%3D{x}%26y%3D{y}%26z%3D{z}'
        rlayer = QgsRasterLayer(urlWithParams, 'Google Satellite', 'wms')
        if rlayer.isValid():
            QgsProject.instance().addMapLayer(rlayer)

    def finished(self, result):
        if result:
            # self.loadSatelliteImage()
            for layer in self.layers:
                QgsProject.instance().addMapLayer(layer)
                tableName = [k for k,v in self.layerDbNames.items() if v == layer.name()]
                self.setLayerStyle(layer, tableName[0])
        else:
            pass
