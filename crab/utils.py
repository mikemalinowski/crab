"""
This contains a series of utility and helper functions which do not 
live under any bespoke module
"""
import pymel.core as pm

from . import config
from . import shapeio


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
def find_above(node, substring):
    """
    Looks for the parent with the given substring in the name

    :param node: Node to search from
    :type node: pm.nt.DagNode

    :param substring: String to look for in a node name
    :type substring: str

    :return: pm.nt.DagNode
    """
    while node:
        if substring in node.name():
            return node

        node = node.getParent()

    return None


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
