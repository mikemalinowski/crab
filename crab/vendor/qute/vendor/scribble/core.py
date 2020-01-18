import os
import sys
import json


# -- This is a special environment variable which the user can set in
# -- order to tailor exactly where scribble will write out its data
ENVIRONMENT_VARIABLE = 'PYSCRIBBLE_STORAGE_DIR'

# -- Determine where we should store our data files. This is dependent
# -- upon a couple of factors. Firstly, we allow for hte user to define
# -- an environment variable which specifies the storage location
STORAGE_DIRECTORY = os.environ.get(ENVIRONMENT_VARIABLE, None)

# -- If we have not been provided with a specific storage location
# -- then we need to resolve to a default location, but this is platform
# -- dependent
if sys.platform == 'linux' or sys.platform == 'linux2':
    if 'XDG_CONFIG_HOME' in os.environ:
        STORAGE_DIRECTORY = os.path.join(
            os.environ['XDG_CONFIG_HOME'],
            'pyscribble',
        )

    else:
        STORAGE_DIRECTORY = os.path.join(
            os.environ['HOME'],
            '.config',
            'pyscribble',
        )

elif sys.platform == 'win32':
    STORAGE_DIRECTORY = os.path.join(
        os.environ.get('APPDATA'),
        'pyscribble',
    )

elif sys.platform == 'darwin':
    STORAGE_DIRECTORY = os.path.join(
        os.environ['HOME'],
        'Documents',
        'pyscribble',
    )

else:
    raise Exception(
        (
            '%s is not supported by default. In order to utilise this module '
            'you must define an environment variable (%s) specifying the '
            'storage path'
        ) % (
            sys.platform,
            ENVIRONMENT_VARIABLE,
        )
    )


# ------------------------------------------------------------------------------
def get(identifier, *args, **kwargs):
    """
    This will attempt to retrieve a Scribble Dictionary from the 
    STORAGE_DIRECTORY. If it does not exist, an empty Scribble 
    Dictionary will be created which will be savable with the given
    identifier.
    
    :param identifier: Unique identifier to access a specific scribble
        dictionary.
    :type identifier: str
    
    :return: ScribbleDictionary
    """
    return ScribbleDictionary(identifier, *args, **kwargs)


# ------------------------------------------------------------------------------
class ScribbleDictionary(dict):

    # --------------------------------------------------------------------------
    def __init__(self, identifier, *args, **kwargs):
        super(ScribbleDictionary, self).__init__(*args, **kwargs)

        # -- Store the identifier, as this is used whenever the
        # -- scribble dictionary is stored.
        self.identifier = identifier

        # -- Initiate a load of any persistent data for the given
        # -- identifier
        self.load()

    # --------------------------------------------------------------------------
    def load(self):
        """
        Loads the data from the disk if it exists and updates this
        dictionary.
        """
        if os.path.exists(self.location()):
            with open(self.location(), 'r') as f:
                self.update(json.load(f))

    # --------------------------------------------------------------------------
    def save(self):
        """
        Saves the ScribbleDictionary data to a persistent state
        """
        # -- Ensure the location to save to exists, otherwise the
        # -- write will fail
        if not os.path.exists(STORAGE_DIRECTORY):
            os.makedirs(STORAGE_DIRECTORY)

        # -- Serialise to json - we wrap this in a try/except in case
        # -- the data is not json serialisable.
        try:
            data = json.dumps(
                self,
                indent=4,
                sort_keys=True,
            )

        except BaseException:
            raise Exception(
                'Could not encode the data within the Scribble Dictionary '
                'to JSON. Please ensure any stored data can be serialised '
                'to JSON.'
            )

        # -- Write the data out
        with open(self.location(), 'w') as f:
            f.write(data)

    # --------------------------------------------------------------------------
    def location(self):
        """
        Returns the location of the persistent file. This is regardless of
        whether the file exists or not.
        
        :return: str
        """
        return os.path.join(
            STORAGE_DIRECTORY,
            '%s.json' % (
                self.identifier,
            ),
        )
