from qgis.core import QgsProject, QgsGeometry, QgsCoordinateReferenceSystem
from qgis.core import QgsFillSymbol, QgsVectorLayer, QgsFeature
from PyQt5.QtCore import QVariant


class AnchorLineTemp():
    """Реализует построение временного слоя линии привязки
    """
    def __init__(self, canvas, point, features, uid):

        self.uid = uid
        self.canvas = canvas
        self.features = features
        self.point = point
        self.projectInstance = QgsProject.instance()
        self.symbol = self.setLayerSymbol()

        self.attributes = [self.uid]
        self.attributesDictionary = {**self.attrDict()}

        self.fieldsString = self.fieldsToString()


    def attrDict(self):
        dictionary = {}
        dictionary["uid"] = self.uid
        return dictionary

    def fieldsToString(self):
        string = "&field=uid"
        return string

    def setLayerSymbol(self):
        symbol = QgsFillSymbol.createSimple(
            {'color': '255,0,0,100', 'color_border': '0,0,0,255'})
        return symbol

    def makeFeature(self):
        self.deleteTempLayerIfExists()
        uri = "linestring?crs=epsg:32635" + self.fieldsString
        layer = QgsVectorLayer(uri, "Привязка временный слой", "memory")

        layer.setCrs(QgsCoordinateReferenceSystem(32635))
        self.projectInstance.addMapLayer(layer)

        feat = QgsFeature()
        countAttributes = len(self.attributesDictionary)
        feat.initAttributes(countAttributes)

        i = 0
        for key in self.attributesDictionary:
            feat[i] = self.attributesDictionary[key]
            i += 1

        feat.setGeometry(QgsGeometry.fromPolylineXY(
            [self.point] + self.features))

        (res, outFeats) = layer.dataProvider().addFeatures([feat])

        layers = self.canvas.layers()
        layers.insert(0, layer)
        self.canvas.setLayers(layers)
        self.canvas.refresh()

        if self.canvas.isCachingEnabled():
            layer.triggerRepaint()
        else:
            self.canvas.refresh()

    def deleteTempLayerIfExists(self):
        try:
            layer = self.projectInstance.mapLayersByName(
                "Привязка временный слой")[0]
            self.projectInstance.removeMapLayers([layer.id()])
        except:
            pass

