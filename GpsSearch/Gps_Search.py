"""This module creates a GPS Search Plugin for QGIS"""
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import (
    QLabel, QDialog, QComboBox, QRadioButton,
    QVBoxLayout, QAction, QLineEdit, QPushButton
    )
from qgis.core import (
    QgsPointXY, QgsCoordinateTransform,
    QgsProject, QgsCoordinateReferenceSystem
    )
from qgis.gui import QgsVertexMarker
from . import resources


class Gps_Search:
    """Main class for plugin"""
    def __init__(self, iface):
        self.iface = iface
        self.scale = 1000
        self.seperator = '/'
        self.dialog = Dialog()
        self.canvas = self.iface.mapCanvas()
        self.marker = QgsVertexMarker(self.canvas)


    def initGui(self):
        self.action = QAction("GpsSearch", self.iface.mainWindow())
        self.iface.addPluginToMenu("&GpsSearch", self.action)
        self.toolbar = self.iface.addToolBar("GpsSearch")
        self.line_edit = MyLineEdit(self.marker)
        self.line_edit.setMaximumWidth(150)
        self.line_edit.returnPressed.connect(self.run)
        self.toolbar.addWidget(self.line_edit)
        self.button = QPushButton("Gps Search")
        self.toolbar.addWidget(self.button)
        ## run when Enter is pressed
        self.button.clicked.connect(self.run)
        ## add setting button
        self.settings = QAction(QIcon(":settings.png"), "Search Settings", self.iface.mainWindow())
        self.toolbar.addAction(self.settings)
        self.settings.triggered.connect(self.settingsDialog)
        self.clear = QAction(QIcon(":eraser.png"), "Clear Markers", self.iface.mainWindow())
        self.toolbar.addAction(self.clear)
        self.clear.triggered.connect(self.clearMarker)

    def unload(self):
        self.iface.removePluginMenu("&GpsSearch", self.action)
        self.iface.removeToolBarIcon(self.settings)

    def run(self):
        #### get the input from line edit
        coords = self.line_edit.text()
        coords = str(coords)
        ## remove whitespace from coords
        coords = coords.lstrip()
        coords = coords.rstrip()
        ## extract x,y values from imput string.
        coord_pair = coords.split(self.dialog.seperator)
        try:
            coord_pair[1]
        except:
            raise ValueError("Invalid Seperator provided")
        ## convert pair to dict
        if self.dialog.latlong_radio.isChecked() == True:
            coord_dict = {'X':float(coord_pair[1]), 'Y':float(coord_pair[0])}
        else:
            coord_dict = {'X':float(coord_pair[0]), 'Y':float(coord_pair[1])}
        ## convert x,y values to a QgsPoint
        point = QgsPointXY(coord_dict["X"], coord_dict["Y"])
        ## get the canvas instance
        #canvas = self.iface.mapCanvas()
        ## transform that point to the current EPSG
        ## set CRS to transfrom point into
        inputSrc = QgsCoordinateReferenceSystem(4326)
        #get the CRS of the current project
        project = QgsProject().instance()
        destSrc = QgsCoordinateReferenceSystem(project.crs().postgisSrid())
        ## transform the point
        xform = QgsCoordinateTransform(inputSrc, destSrc, project)
        newPoint = xform.transform(point)
        ## Place marker
        self.marker.setCenter(newPoint)
        self.marker.setColor(QColor(255,192,203))
        self.marker.setIconSize(16)
        self.marker.setIconType(QgsVertexMarker.ICON_CIRCLE)
        self.marker.setPenWidth(3)
        self.marker.show()
        ### center and scale map
        self.canvas.setCenter(newPoint)
        self.canvas.zoomScale(self.dialog.scale)

    def settingsDialog(self):
        self.dialog.show()

    def clearMarker(self):
        self.marker.hide()


class Dialog(QDialog):
    def __init__(self):
        super(Dialog, self).__init__()
        ## Setup Vars
        self.seperator = '/'
        self.scale = 1000
        ## Seperator ComboBox setup
        self.sep_combo = QComboBox()
        self.sep_list = ["/", "\\", ";", ":", ",", " "]
        #self.sep_list_names = ["Forwardslash /", "Backslash \\", "Semicolon ;", "Colon :", "Comma ,", "Space"]
        self.sep_list_names = ["/   Forwardslash", "\\   Backslash", ";   Semicolon", ":   Colon", ",   Comma", "Space"]
        self.sep_combo.addItems(self.sep_list_names)
        index = self.sep_list.index(self.seperator)
        self.sep_combo.setCurrentIndex(index)
        self.sep_combo.currentTextChanged.connect(self.changeSeperator)
        ## Scale ComboBox setup
        self.scale_combo = QComboBox()
        self.scale_list = ['250', '500', '1000', '2000']
        self.scale_combo.addItems(self.scale_list)
        index = self.scale_combo.findText(str(self.scale))
        self.scale_combo.setCurrentIndex(index)
        self.scale_combo.currentTextChanged.connect(self.changeScale)
        ## Coordinate Format Setup
        self.latlong_radio = QRadioButton("Latitude / Longitude (Default)")
        self.latlong_radio.setChecked(True)
        self.longlat_radio = QRadioButton("Longitude / Latitude")
        # ## Layout setup
        self.layout = QVBoxLayout()
        self.label_1 = QLabel("Seperator...")
        self.layout.addWidget(self.label_1)
        self.layout.addWidget(self.sep_combo)
        self.label_2 = QLabel("Scale...")
        self.layout.addWidget(self.label_2)
        self.layout.addWidget(self.scale_combo)
        self.label_3 = QLabel("Coordinate Format...")
        self.layout.addWidget(self.label_3)
        self.layout.addWidget(self.latlong_radio)
        self.layout.addWidget(self.longlat_radio)
        self.setLayout(self.layout)
        self.setWindowTitle("Settings")

    def changeSeperator(self):
        i = self.sep_combo.currentIndex()
        self.seperator = self.sep_list[i]

    def changeScale(self):
        self.scale = int(self.scale_combo.currentText())


class MyLineEdit(QLineEdit):
    def __init__(self,marker):
        super(QLineEdit,self).__init__()
        self.marker = marker
    def focusInEvent(self,e):
        self.marker.hide()
