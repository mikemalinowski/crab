from ..vendor.Qt.QtGui import QPixmap, QImage
from ..vendor.Qt.QtCore import QByteArray, QDataStream, QIODevice

from ..vendor import Qt


# --------------------------------------------------------------------------
def toGrayscale(pixmap):
    """
    Creates a new pixmap which is a grayscale version of the given
    pixmap

    :param pixmap: QPixmap

    :return: QPixmap
    """
    # -- Get an image object
    image = pixmap.toImage()

    # -- Cycle the pixels and convert them to grayscale
    for x in range(image.width()):
        for y in range(image.height()):

            # -- Grayscale the pixel
            gray = Qt.QtGui.qGray(
                image.pixel(
                    x,
                    y,
                ),
            )

            # -- Set the pixel back into the image
            image.setPixel(
                x,
                y,
                Qt.QtGui.QColor(
                    gray,
                    gray,
                    gray,
                ).rgb()
            )

    # -- Re-apply the alpha channel
    image.setAlphaChannel(
        pixmap.toImage().alphaChannel()
    )

    # -- Return the pixmap
    return Qt.QtGui.QPixmap.fromImage(image)
