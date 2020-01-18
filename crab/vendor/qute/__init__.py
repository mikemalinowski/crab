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
__version__ = "1.0.11"

# -- Import all our Qt variables into this namespace - which
# -- makes it trivial to use later
from .vendor.Qt.QtCore import *
from .vendor.Qt.QtGui import *
from .vendor.Qt.QtWidgets import *

# -- We import QtCompat explicitly
from .vendor.Qt import QtCompat

from ._utils import slimify
from ._utils import qApp
from ._utils import toGrayscale
from ._utils import emptyLayout
from ._utils import addLabel
from ._utils import getComboIndex

from ._style import applyStyle
from ._style import getCompoundedStylesheet

from ._menu import menuFromDictionary

from ._derive import deriveWidget
from ._derive import deriveValue
from ._derive import setBlindValue
from ._derive import connectBlind

from ._windows import mainWindow
from ._windows import MemorableWindow

from ._events import printEventName

from ._ui import loadUi

from . import quick
from . import constants


