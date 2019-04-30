"""
Crab is a component based rigging framework which allows for
rigs to be build from modular parts.

NOTE: Crab is still in development!

Crab can be extended using three main plugin types:

* Component
    A component is a hierarchical rig element which is represented by a 
    skeleton structure and is capable of building a control rig over the top.
    A component can also optionally build a guide over itself to make editing
    the skeletal structure easier.
    
    You can read more about components by looking in crab.component

* Behaviour
    A behaviour is a rigging behaviour which may or may not have a dag element
    to it and may be dependent on other elements of the control rig. Whilst
    components are atomic behaviours can cross the boundaries of any component.

* Process
    A process is a plugin which is executed during an edit call as well as
    a build call. This plugin type has three stages:
    
        * snapshot
            This is done before the control rig is destroyed and its your
            oppotunity to read any information from the rig. 
            Note: You must store the data you have read, as the same process
                instance will not be used during the build.
        
        * pre
            This is called after the control is destroyed, leaving the skeleton
            bare. This is typically a good time to do any skeleton modifications
            as nothing will be locking or driving the joints.
        
        * post
            This is called after all the components and behaviours are built, 
            allowing  you to perform any actions against the rig as a whole.


Crab comes with a rig building interface built in, therefore if you just
want to utilise crab as a tool you can do:

```python
import crab
crab.creator.launch()
```

However, the creator interface is just a ui which sits atop of crab, so 
everything you can do in the ui you can also do through code. For instance
to create a new rig...

```python
import crab

new_rig = crab.Rig.create('MyRig')
```

In the following example we will create a new rig, add a component and then
build the rig before re-editing the rig.

```python
import crab

# -- Create a new rig
new_rig = crab.Rig.create('MyRig')

# -- Add some components to the rig
next_parent = None
for idx in range(5):
    new_rig.add_component('Singular', parent=next_parent, description='Demo')
    next_parent = pm.selected()[0]

# -- We now have a rig with 5 components, lets build
# -- our rig...
new_rig.build()

# -- Finally, lets restore our rig to an editable
# -- state
new_rig.edit()
```


Todo:
    * Mirror Component
    * Layers Post Process
    * Space Switch Post Process
"""
from .rig import Rig
from .component import Component
from .behaviour import Behaviour
from .process import Process

from . import config
from . import utils
from . import shapeio
from . import create

from .apps import creator

