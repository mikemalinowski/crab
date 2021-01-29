"""
This holds a set of constant variables for qute
"""
import os
import logging

from . import resources

log = logging.getLogger('qute')


# -- This is the name of the environment variable we will
# -- check for
QUTE_STYLE_PATH = 'QUTE_STYLE_PATH'

# -- This will look at the environment variable for styles and pull
# -- out a resolved list of those locations which exist
QUTE_STYLE_LOCATIONS = [
    location.strip()
    for location in os.environ.get(
        QUTE_STYLE_PATH,
        ''
    ).split(os.path.pathsep)
    if os.path.isdir(location.strip())
]

QUTE_STYLE_LOCATIONS.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        'styles',
    ),
)

# -- This is a set of default variables used when
# -- applying style sheets
STYLE_DEFAULTS = {
    '_BACKGROUND_': '40, 40, 40',
    '_ALTBACKGROUND_': '70, 70, 70',
    '_FOREGROUND_': '66, 194, 244',
    '_HIGHLIGHT_': '109, 214, 255',
    '_TEXT_': '255, 255, 255',
}

# -- We expose all of our resources as special variables
for resource in resources.all():
    key = '_%s_' % os.path.basename(resource).replace('.', '_').upper()
    STYLE_DEFAULTS[key] = resource

