# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VectorToRaster
                                 A QGIS plugin
 This plugin converts .shp Vector files to .tif Raster files.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-01-20
        copyright            : (C) 2020 by Rohit Handique
        email                : rohand.181cv135@nitk.edu.in
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load VectorToRaster class from file VectorToRaster.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .vector_to_raster import VectorToRaster
    return VectorToRaster(iface)
