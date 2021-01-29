"""
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
"""
qute is an extension to the Qt.py module written by Marcus Ottosson and
can be found here:
https://github.com/mottosso/Qt.py

This extension aims to expose additional help utilities to Qt which are
common place within coding projects.
"""
__author__ = "Michael Malinowski"
__copyright__ = "Copyright (C) 2019 Michael Malinowski"
__license__ = "MIT"
__version__ = "3.0.10"

import imp

# -- Import all our Qt variables into this namespace - which
# -- makes it trivial to use later
from .vendor.Qt.QtCore import *
from .vendor.Qt.QtGui import *
from .vendor.Qt.QtWidgets import *
from .vendor.Qt import QtCompat

from . import extensions
from . import utilities
from . import constants


# ------------------------------------------------------------------------------
# All imports below this line are deprecated imports which are still exposed
# for backward compatibility between version 1.0.11 and 2.0.1
# You should not use these imports.

# -- We import QtCompat explicitly

from .utilities.layouts import slimify
from .utilities import qApp
from .utilities.pixmaps import toGrayscale
from .utilities.layouts import empty as emptyLayout
from .utilities.widgets import addLabel
from .utilities.widgets import getComboIndex
from .utilities.widgets import setComboByText

from .utilities.styling import apply as applyStyle
from .utilities.styling import getCompoundedStylesheet

from .utilities.menus import menuFromDictionary

from .utilities.derive import deriveWidget
from .utilities.derive import deriveValue
from .utilities.derive import setBlindValue
from .utilities.derive import connectBlind

from .utilities.windows import mainWindow
from .extensions.windows import MemorableWindow

from .utilities.events import printEventName

from .utilities.designer import load as loadUi

from .utilities.launch import quick_app

from .extensions.tray import TimedProcessorTray
from .extensions.tray import MemorableTimedProcessorTray

# -- Quick was a convenience sub-module which became a little
# -- too convenient to put things. Therefore its contents is
# -- now spread around. However, for the sake of backward compatability
# -- we need to nest its functionality in a placeholder class
from .utilities.request import confirmation as _rerouted_confirm
from .utilities.request import text as _rerouted_getText
from .utilities.request import filepath as _rerouted_getFilepath
from .utilities.request import folderpath as _rerouted_getFolderPath
from .extensions.dividers import HorizontalDivider as _rerouted_horizontalDivider
from .extensions.buttons import CopyToClipboardButton as _rerouted_copyToClipBoardButton

quick = imp.new_module('qute.quick')

quick.confirm = _rerouted_confirm
quick.getText = _rerouted_getText
quick.getFilepath = _rerouted_getFilepath
quick.getFolderPath = _rerouted_getFolderPath
quick.horizontalDivider = _rerouted_horizontalDivider
quick.copyToClipBoardButton = _rerouted_copyToClipBoardButton
quick.quick_app = quick_app
