import pymel.core as pm


# ------------------------------------------------------------------------------
# -- This is a list of Component types. These are used in META nodes
# -- to define the type of component (such as guide, skeleton etc)
COMPONENT_MARKER = 'crabComponent'


# ------------------------------------------------------------------------------
# -- This is a list of names which define attributes on meta nodes.
META_IDENTIFIER = 'Identifier'
META_VERSION = 'Version'
META_OPTIONS = 'Options'
META_CONTENTS = 'Contents'

# ------------------------------------------------------------------------------
# -- This is a list of attribute names used by the internals of
# -- crab to resolve relationships between objects
BOUND = 'crabBinding'
BEHAVIOUR_DATA = 'crabBehaviours'

# ------------------------------------------------------------------------------
RIG_ROOT_LINK_ATTR = 'crabRigHost'
CONNECTION_PREFIX = 'crabRootConnection'
SKELETON_ROOT_LINK_ATTR = '%sSkeleton' % CONNECTION_PREFIX
CONTROL_ROOT_LINK_ATTR = '%sControls' % CONNECTION_PREFIX
GUIDE_ROOT_LINK_ATTR = '%sGuide' % CONNECTION_PREFIX


# ------------------------------------------------------------------------------
# -- This is a group of layer names
HIDDEN_LAYER = 'Hidden'
CONTROL_LAYER = 'Controls'
SKELETON_LAYER = 'Skeleton'
GEOMETRY_LAYER = 'Geometry'

# ------------------------------------------------------------------------------
# -- This is a list of name prefixes for structural objects created
# -- within a crab rig hierarchy
RIG_ROOT = 'RIG'
RIG_COMPONENT = 'CMP'
GUIDE_COMPONENT = 'GCM'
META = 'META'

# ------------------------------------------------------------------------------
# -- This is a list of pre-fixes for general use within a crab plugin
# -- in order to keep naming consistent
ORG = 'ORG'
CONTROL = 'CTL'
ZERO = 'ZRO'
OFFSET = 'OFF'
SKELETON = 'SKL'
MECHANICAL = 'MEC'
MATH = 'MATH'
MARKER = 'LOC'
GUIDE = 'GDE'
PIVOT = 'PIV'
LOGIC = 'LGC'
SNAP = 'SNP'
IK = 'IKH'
EFFECTOR = 'EFF'
CLUSTER = 'CLS'
UPVECTOR = 'UPV'
SPLINE = 'CRV'
CONSTRAINT = 'CNS'
CONSTRAINTGROUP = 'CNSG'

PREFIXES = [
    ORG,
    CONTROL,
    ZERO,
    OFFSET,
    SKELETON,
    MECHANICAL,
    MATH,
    MARKER,
    GUIDE,
    PIVOT,
    LOGIC,
    SNAP,
    IK,
    EFFECTOR,
    CLUSTER,
    UPVECTOR,
    SPLINE,
    CONSTRAINT,
    CONSTRAINTGROUP,
]

# ------------------------------------------------------------------------------
# -- This is a list of suffixes for general use within a crab plugin
# -- in order to keep naming consistent
# -- Sides and Locations
LEFT = 'LF'
RIGHT = 'RT'
MIDDLE = 'MD'
FRONT = 'FR'
BACK = 'BK'
TOP = 'TP'
BOTTOM = 'BT'
SIDELESS = 'NA'

LOCATIONS = [
    LEFT,
    RIGHT,
    MIDDLE,
    FRONT,
    BACK,
    TOP,
    BOTTOM,
    SIDELESS,
]

# ------------------------------------------------------------------------------
# -- Define colours based on categories
LEFT_COLOR = [252, 48, 1]
RIGHT_COLOR = [0, 162, 254]
MIDDLE_COLOR = [254, 209, 0]
NON_ANIMATABLE_COLOUR = [150, 150, 150]
GUIDE_COLOR = [162, 222, 0]

# ------------------------------------------------------------------------------
# -- Defines attribute defaults
DEFAULT_CONTROL_ROTATION_ORDER = 5

# ------------------------------------------------------------------------------
# -- Defines attribute defaults
OWNED_LAYERS = [
    'Hidden',
    'Controls',
    'Skeleton',
    'Geometry',
]


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
def name(prefix, description, side, counter=1):
    """
    Generates a unique name with the given naming parts

    :param prefix: Typically this is used to denote usage type. Note that this
        should not be 'node type' but should be representative of what the node
        is actually being used for in the rig.
    :type prefix: str

    :param description: This is the descriptive element of the rig and should
        ideally be upper camel case.
    :type description: str

    :param side: This is the location of the element, such as LF, RT  or MD etc
    :type side: str

    :param counter: To ensure all names are unique we use a counter. By default
        all counters start at 1, but you may override this.
    :type counter: int

    :return:
    """
    while True:
        candidate = '%s_%s_%s_%s' % (
            prefix.upper(),
            description,
            counter,
            side.upper(),
        )

        # -- If the name is unique, return it
        if not pm.objExists(candidate):
            return candidate

        # -- The name already exists, so increment our
        # -- counter
        counter += 1


# ------------------------------------------------------------------------------
def get_prefix(given_name):
    """
    Assuming the given name adheres to the naming convention of crab this
    will extract the prefix element of the name.

    :param given_name: Name to extract from
    :type given_name: str or pm.nt.DependNode

    :return: str
    """
    return str(given_name).split(':')[-1].split('_')[0]


# ------------------------------------------------------------------------------
def get_description(given_name):
    """
    Assuming the given name adheres to the naming convention of crab this
    will extract the descriptive element of the name.

    :param given_name: Name to extract from
    :type given_name: str or pm.nt.DependNode

    :return: str
    """
    return str(given_name).split(':')[-1].split('_')[1]


# ------------------------------------------------------------------------------
def get_counter(given_name):
    """
    Assuming the given name adheres to the naming convention of crab this
    will extract the counter element of the name.

    :param given_name: Name to extract from
    :type given_name: str or pm.nt.DependNode

    :return: int
    """
    parts = given_name.split('_')

    for part in parts:
        if part.isnumeric():
            return int(part)

    return None


# ------------------------------------------------------------------------------
def get_side(given_name):
    """
    Assuming the given name adheres to the naming convention of crab this
    will extract the side/location element of the name.

    :param given_name: Name to extract from
    :type given_name: str or pm.nt.DependNode

    :return: str
    """
    parts = given_name.split('_')

    if not parts:
        return ''

    return parts[-1]
