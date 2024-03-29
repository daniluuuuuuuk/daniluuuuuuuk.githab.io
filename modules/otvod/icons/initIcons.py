import os
from PyQt5.QtGui import QIcon


class IconSet:
    def __init__(self, omw):
        self.omw = omw
        self.omw.peekFromMap_PushButton.setIcon(
            QIcon(self.resolve("pick_from_map_icon.png"))
        )
        self.omw.peekFromGPSPushButton.setIcon(
            QIcon(self.resolve("pick_from_gps_icon.png"))
        )
        self.omw.azimuthTool_pushButton.setIcon(
            QIcon(self.resolve("azimuth_icon.png"))
        )
        self.omw.movePoint_button.setIcon(
            QIcon(self.resolve("move_tool.png"))
        )        
        self.omw.buildLesoseka_Button.setIcon(QIcon(self.resolve("build.png")))
        self.omw.editAttributes_button.setIcon(
            QIcon(self.resolve("pencil.png"))
        )
        self.omw.saveLesoseka_Button.setIcon(QIcon(self.resolve("save.png")))
        self.omw.deleteLesoseka_Button.setIcon(
            QIcon(self.resolve("delete.png"))
        )
        self.omw.generateReport_Button.setIcon(
            QIcon(self.resolve("report.png"))
        )
        self.omw.peekVydelFromMap_pushButton.setIcon(
            QIcon(self.resolve("pin.png"))
        )
        self.omw.lesoseka_from_map_button.setIcon(
            QIcon(self.resolve("lesoseka_from_map.png"))
        )
        self.omw.lesoseka_from_map_points_button.setIcon(
            QIcon(self.resolve("lesoseka_from_map_points.png"))
        )
        self.omw.exportAsImage_PushButton.setIcon(
            QIcon(self.resolve("image.png"))
        )
        self.omw.gpsTablet_pushButton.setIcon(
            QIcon(self.resolve("gps.png"))
        )        
        self.omw.handTool_button.setIcon(QIcon(self.resolve("hand_tool.png")))
        self.omw.manageLayers_button.setIcon(QIcon(self.resolve("layers.png")))
        self.omw.saveData_pushButton.setIcon(QIcon(self.resolve("save.png")))
        self.omw.loadData_pushButton.setIcon(QIcon(self.resolve("upload.png")))
        self.omw.magneticDeclination_pushButton.setIcon(
            QIcon(self.resolve("magnet.png"))
        )

    def resolve(self, name, basepath=None):
        if not basepath:
            basepath = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(basepath, name)
