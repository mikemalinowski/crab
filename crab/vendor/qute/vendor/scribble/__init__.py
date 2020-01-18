"""
Scribble is a mechanism to store dictionary information to a persistent
state. This allows the data to be easily retrieved and edited, making it
a good option when trying to store settings data. 

Note: Data saved within the ScribbleDictionary must be json serialisable.

An example of creating a persisten data block would be:

..code-block:: python

    import os
    import scribble
    
    
    # -- Instance a scribble dictionary. We can treat this exactly
    # -- as we treat a dictionary
    data = scribble.get('foobar')
    
    # -- Set some key/value pairs in the ScribbleDictionary
    data['option_a'] = True
    data['option_b'] = 123
    
    # -- Calling .save() will trigger the dictionary
    # -- to store its current state to a persistent state
    data.save()
    
    # -- We can see the location the data is saved to, and we can
    # -- see that it does indeed exist
    print(data.location())
    print(os.path.exists(data.location()))
    
    
Equally, we can re-retrieve that data in a completely new instance of python
using the following code:

..code-block:: python

    # -- Instance a scribble dictionary with the same identifier
    data = scribble.get('foobar')
    
    # -- Print the fact that we have retrieved the same 
    # -- infromation
    print(data)
    # {'option_a': True, 'option_b': 123}
    
    # -- We can then further edit the data
    data['option_a'] = False
    
    # -- Calling .save() will trigger the dictionary
    # -- to store its current state to a persistent state
    data.save()
    
By default scribble will store its data in the follow platform specific
locations:

    * Windows: %APPDATA%/pyscribble
    
    * Linux: %XDG_CONFIG_HOME%/pyscribble if the environment variable exists, otherwise %HOME%/.config/pyscribble
    
    * OSX: Not yet supported

However, you can override these paths by setting an environment variable
PYSCRIBBLE_STORAGE_DIR, if this is set then the path defined by that variable
will always be used over the default behaviour.
"""
from .core import get
