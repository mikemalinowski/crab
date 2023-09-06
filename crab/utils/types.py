# --------------------------------------------------------------------------------------
class AttributeDict(dict):
    """
    An AttributeDict is a dictionary where by its members can be accessed as
    properties of the class.


        .. code-block:: python

            >>> ad = AttributeDict()
            >>> ad["foo"] = 10

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
