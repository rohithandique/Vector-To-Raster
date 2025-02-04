# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VectorToRaster
                                 A QGIS plugin
 This plugin converts .shp Vector files to .tif Raster files.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-01-20
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Rohit Handique
        email                : rohand.181cv135@nitk.edu.in
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
#Importing necessary modules
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsProject, Qgis
from PyQt5.QtWidgets import QAction, QFileDialog

#Importing the modules for conversion
from osgeo import gdal
from osgeo import ogr
from osgeo import osr

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .vector_to_raster_dialog import VectorToRasterDialog
import os.path


class VectorToRaster:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'VectorToRaster_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Vector To Raster')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('VectorToRaster', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/vector_to_raster/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Convert Vector to Raster'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Vector To Raster'),
                action)
            self.iface.removeToolBarIcon(action)



    def select_output_file(self):
        filename, _filter = QFileDialog.getSaveFileName(
            self.dlg, "Save As ","", '*.tif')
        self.dlg.lineEdit.setText(filename)
        

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = VectorToRasterDialog()
            self.dlg.pushButton.clicked.connect(self.select_output_file)

        
        # Fetch the currently loaded layers
        layers = QgsProject.instance().layerTreeRoot().children()
        # Clear the contents of the comboBox from previous runs
        self.dlg.comboBox.clear()
        # Populate the comboBox with names of all the loaded layers
        self.dlg.comboBox.addItems([layer.name() for layer in layers])
        # Access selected layer
        raster_name = self.dlg.comboBox.currentText()
        raster_layer = QgsProject().instance().mapLayersByName(raster_name)[0]
        path = raster_layer.source()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed

        output_raster = self.dlg.lineEdit.text()

        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            #making the shapefile as an object.
            input_shp = ogr.Open(path)

            #getting layer information of shapefile.
            shp_layer = input_shp.GetLayer()

            #pixel_size determines the size of the new raster.
            #pixel_size is proportional to size of shapefile.
            pixel_size = 1

            #get extent values to set size of output raster.
            x_min, x_max, y_min, y_max = shp_layer.GetExtent()

            #calculate size/resolution of the raster.
            x_res = int((x_max - x_min) / pixel_size)
            y_res = int((y_max - y_min) / pixel_size)

            #get GeoTiff driver by
            image_type = 'GTiff'
            driver = gdal.GetDriverByName(image_type)

            #passing the filename, x and y direction resolution, no. of bands, new raster.
            new_raster = driver.Create(output_raster, x_res, y_res, 1, gdal.GDT_Byte)

            #transforms between pixel raster space to projection coordinate space.
            new_raster.SetGeoTransform((x_min, pixel_size, 0, y_min, 0, pixel_size))

            #get required raster band.
            band = new_raster.GetRasterBand(1)

            #assign no data value to empty cells.
            no_data_value = -9999
            band.SetNoDataValue(no_data_value)
            band.FlushCache()

            #main conversion method
            gdal.RasterizeLayer(new_raster, [1], shp_layer, burn_values=[255])

            #adding a spatial reference
            new_rasterSRS = osr.SpatialReference()
            new_rasterSRS.ImportFromEPSG(2975)
            new_raster.SetProjection(new_rasterSRS.ExportToWkt())

            self.iface.messageBar().pushMessage("Success", "Output File Written at " + output_raster, level=Qgis.Success, duration=3)

            return gdal.Open(output_raster)