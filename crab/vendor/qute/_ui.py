# noinspection PyPep8Naming
import xml.etree.ElementTree as exml

from .vendor import Qt


# ------------------------------------------------------------------------------
# noinspection PyPep8Naming,PyUnresolvedReferences,PyBroadException
def loadUi(ui_file, base_instance=None):
    try:
        return Qt.QtCompat.loadUi(ui_file, base_instance)

    except:

        # -- For applications such as 3dsmax we have to compile the
        # -- ui differently
        try:
            import pyside2uic as pyuic
            from cStringIO import StringIO

        except:
            raise Exception('No implementation for loadUi found.')

        # -- Read out the xml file
        xml_data = exml.parse(ui_file)

        # -- Get the lcass of the widget and the form
        widget_class = xml_data.find('widget').get('class')
        form_class = xml_data.find('class').text

        # -- Open the ui file as text
        with open(ui_file, 'r') as f:

            # -- Create a file like object
            o = StringIO()
            frame = {}

            # -- Compile the ui into compiled python and execute it
            pyuic.compileUi(f, o, indent=0)
            pyc = compile(o.getvalue(), '<string>', 'exec')
            eval('exec pyc in frame')

            # -- Get the form class
            form_class = frame['Ui_%s' % form_class]

            # -- Alter what we're evaulating based on what version
            # -- of qt we're running
            try:
                base_class = eval('Qt.QtGui.%s' % widget_class)

            except (NameError, AttributeError):
                base_class = eval('Qt.QtWidgets.%s' % widget_class)

        # -- Subclass the loaded classes to build a wrapped widget
        class _WrappedHelper(form_class, base_class):
            # noinspection PyShadowingNames
            def __init__(self, parent=None):
                super(_WrappedHelper, self).__init__(parent)
                self.setupUi(self)

        return _WrappedHelper()
