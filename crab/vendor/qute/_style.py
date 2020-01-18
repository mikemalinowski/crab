"""
This module holds functionality to apply and generate styling information
to widgets
"""
import os
import re

from . import _utils
from . import constants


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
def applyStyle(styles, apply_to, **kwargs):
    """
    Applies all the given styles in order (meaning each will override any
    overlapping elements of the previous).
    
    All kwargs are considered replacements when wrangling your stylesheet. 
    This allows you to place variables into your css file and have them resolved
    at runtime.
    
    :param styles: This can be a single stylesheet or a list of stylesheets.
        The stylesheet can be given in three different forms (and is checked
        in this order):
        
            * An absolute filepath to a css/qss file
            
            * A Name of any stylesheet which exists in any location defined
                within the QUTE_STYLE_PATH environment variable
            
            * Actual stylesheet data
    :type styles: This can be given either a single string or a list of 
        strings

    :param apply_to: The QWidget which should have the stylesheet applied
    :type apply_to: QWidget

    :return: None


    .. code-block:: python

        >>> import qute as sk
        >>>
        >>> # -- Ensure we have an application
        >>> if not sk.QtWidgets.QApplication.instance():
        ...     q_app = sk.QtWidgets.QApplication([])
        >>>
        >>> # -- Create a widget
        >>> button = sk.QtWidgets.QPushButton()
        >>> sk.styles.applyStyle("flame", button)

    """
    # -- As we allow single elements or a list of elements to be
    # -- passed we need to conform that now
    styles = _utils.toList(styles)
    available_styles = None

    # -- Start collating our style data
    compounded_style = ''

    for given_style in styles:

        extracted_style = None

        # -- Firstly we check if we're given an absolute path which
        # -- resolves
        if os.path.exists(given_style):
            with open(given_style, 'r') as f:
                extracted_style = f.read()

        # -- If we did not extract a style we need to check the locations
        # -- in our environment path
        if not extracted_style:

            # -- Read out the available styles if it is our first iteration
            # -- during this call
            available_styles = available_styles or _getAvailableStyles()

            # -- If we have the given style we store it
            if given_style in available_styles:
                with open(available_styles[given_style], 'r') as f:
                    extracted_style = f.read()

        # -- Finally we need to check if we think this might be a
        # -- style in its own right
        if not extracted_style and ';' in given_style:
            extracted_style = given_style

        # -- If we still do not have an extracted style then we need
        # -- to report a warning
        if not extracted_style:
            constants.log.warning(
                'Could not extract or locate the style : %s' % given_style
            )
            continue

        # -- Add this extracted data to the compounded style
        compounded_style += '\n' + extracted_style

    # -- We need to combine the kwargs with the defaults
    styling_parameters = constants.STYLE_DEFAULTS.copy()
    styling_parameters.update(kwargs)

    # -- Now that we have compounded all our style information we can cycle
    # -- over it and carry out any replacements
    for regex, replacement in styling_parameters.items():
        regex = re.compile(regex)
        compounded_style = regex.sub(replacement, compounded_style)

    # -- Apply the composed stylesheet
    apply_to.setStyleSheet(compounded_style)


# ------------------------------------------------------------------------------
def getCompoundedStylesheet(widget):
    """
    This will return the entire stylesheet which is affecting this widget. 
    The resulting stylesheet will be the widgets stylesheet, and the 
    stylesheet of all its parents.
    
    The order is such that the widgets style is last, and the root level
    widgets style is first - meaning you can apply the returned stylesheet
    to create the exact same result.
    
    :param widget: Widget to read the style from
    :type widget: QWidget
    
    :return: stylesheet data
    :rtype: str
    """
    all_data = [widget.styleSheet()]

    while widget.parentWidget():

        # -- Iterate to the parent
        widget = widget.parentWidget()

        # -- Take the stylesheet, or an empty string if there
        # -- is no stylesheet
        all_data.append('' or widget.styleSheet())

    # -- Now we reverse the list, so the base parent comes first and the leaf
    # -- style comes last
    all_data.reverse()

    # -- Finally, we join it all together into a single string
    all_data = '\n'.join(all_data)

    return all_data


# ------------------------------------------------------------------------------
def _getAvailableStyles():
    """
    This will look at all the stylesheet locations on the environment path
    and return a dictionary of them, where the key is the name (without a qss
    or css suffix) and the value is the absolute path.
    
    Where there is a name clash, the last will always override the first.
    
    The order of searching is done by the order of paths defined in the 
    QUTE_STYLE_PATH environment variable.
    
    :return: 
    """
    styles = dict()

    for location in constants.QUTE_STYLE_LOCATIONS:

        # -- Skip it if it is not accessible
        if not os.path.exists(location):
            continue

        # -- Cycle over the files in the location
        for style_name in os.listdir(location):

            test_name = style_name.lower()

            # -- Only check for qss or css files
            if test_name.endswith('.css') or test_name.endswith('.qss'):
                styles[style_name[:-4]] = os.path.join(location, style_name)

    return styles
