"""
This contains a series of utility and helper functions which do not 
live under any bespoke module
"""
import pymel.core as pm


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
    :type given_name: str
    
    :return: str 
    """
    return given_name.split('_')[0]


# ------------------------------------------------------------------------------
def get_description(given_name):
    """
    Assuming the given name adheres to the naming convention of crab this
    will extract the descriptive element of the name.
    
    :param given_name: Name to extract from
    :type given_name: str
    
    :return: str 
    """
    return given_name.split('_')[1]


# ------------------------------------------------------------------------------
def get_counter(given_name):
    """
    Assuming the given name adheres to the naming convention of crab this
    will extract the counter element of the name.
    
    :param given_name: Name to extract from
    :type given_name: str
    
    :return: int 
    """
    return int(given_name.split('_')[2])


# ------------------------------------------------------------------------------
def get_side(given_name):
    """
    Assuming the given name adheres to the naming convention of crab this
    will extract the side/location element of the name.
    
    :param given_name: Name to extract from
    :type given_name: str
    
    :return: str 
    """
    return given_name.split('_')[3]


# ------------------------------------------------------------------------------
def create(node_type,
           prefix,
           description,
           side,
           parent=None,
           xform=None,
           match_to=None):
    """
    Convenience function for creating a node, generating the name using
    the unique name method and giving the ability to assign the parent and
    transform.

    :param node_type: Type of node to create, such as 'transform'
    :type node_type: str
    
    :param prefix: Prefix to assign to the node name
    :type prefix: str
    
    :param description: Descriptive section of the name
    :type description: str
    
    :param side: Tag for the location to be used during the name generation
    :type side: str
    
    :param parent: Optional parent to assign to the node
    :type parent: pm.nt.DagNode
    
    :param xform: Optional worldSpace matrix to apply to the object
    :type xform: pm.dt.Matrix
    
    :param match_to: Optional node to match in worldspace
    :type match_to: pm.nt.DagNode
    
    :return: pm.nt.DependNode
    """
    # -- Create the node
    node = pm.createNode(node_type)

    # -- Name it based on our naming convention
    node.rename(
        name(
            prefix=prefix,
            description=description,
            side=side,
        ),
    )

    # -- Parent the node if we're given a parent
    if parent:
        node.setParent(parent)

    # -- If we're given a matrix utilise that
    if xform:
        node.setMatrix(
            xform,
            worldSpace=True,
        )

    # -- Match the object to the target object if one
    # -- is given.
    if match_to:
        node.setMatrix(
            match_to.getMatrix(worldSpace=True),
            worldSpace=True,
        )

    return node


# ------------------------------------------------------------------------------
class AttributeDict(dict):
    """
    An AttributeDict is a dictionary where by its members can be accessed as
    properties of the class.


        .. code-block:: python

            >>> ad = AttributeDict()
            >>> ad['foo'] = 10

            >>> print(ad.foo)
            10

            >>> ad.foo = 5
            >>> ad.foo
            5
    """

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(AttributeDict, self).__init__(*args, **kwargs)

        self.__dict__ = self
        # -- Convert all children to attribute accessible
        # -- dictionaries
        for key in self.keys():
            if type(self[key]) == dict:
                self[key] = AttributeDict(self[key])

            if type(self[key]) == list:
                for i in range(len(self[key])):
                    if type(self[key][i]) == dict:
                        self[key][i] = AttributeDict(self[key][i])

    # --------------------------------------------------------------------------
    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
