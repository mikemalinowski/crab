# Overview

Crab is a Modular Rigging tool for Autodesk Maya. It allows a user
to construct rigs from components (examples of components might be
an arm, spine, leg, singular bone etc). Each component is formed of
a contionous skeletal structure (using joints) from which a control
rig is built over the top.

There is then the concept of Behaviours which can be thought of as
modifiers over a control which allow for rich rig behaviours to be
constructed across component boundries.

The end result is a rigging framework which is capable of generating
deformation and control rigs suitable for most standard game engines
(such as Unreal and Unity).

Furthermore Crab offers tools to assist in the process of rigging along
with a suite of tools geared toward the animator when interacting and
animating a Crab rig.

![alt text](https://raw.githubusercontent.com/mikemalinowski/crab/master/crab/resources/crab_overview.png)

__WARNING:__
    ```
    This should be considered Pre-Release at this stage and comes packaged 
    with only two components and one behaviour for experimentation purposes. 
    ```

## Using the documentation

There are three types of users who are likely to utilise crab, these
being Riggers; Animators and Developers. Each of these users requires
different information, therefore this page has been split into three
parts:

    * Rigging With Crab

    * Crab Animation Tools

    * Extending Crab

<br><br><br><br><br><br>
![alt text](https://raw.githubusercontent.com/mikemalinowski/crab/master/crab/resources/breaker.png)
## Installing and Launching

The easiest way to use crab is to download the crab directory from
this github page, and unzip the file into your _Maya Scripts Location_
which will likely be on a path similar to this:

```
c:/users/your_name/documents/maya/scripts
```

Once you have unziped the file to that location you should launch
maya and run the following:

```python
import crab

crab.creator.launch()
```

Running this should show you the Crab Rigging UI. Alternatively if you
want to launch the animation interface you should run:

```python
import crab

crab.animator.launch()
```

Providing the interfaces launch, crab has been successfully installed.


<br><br><br><br><br><br>
![alt text](https://raw.githubusercontent.com/mikemalinowski/crab/master/crab/resources/breaker.png)
# Rigging With Crab

Crab aims to make rigging easier and less repetative. It does this by
utilising a library of components which generate parts of a rig which
can be hooked together.


## Preconceptions & Assumptions
Before diving into the rigging process with Crab its worth taking a
moment to familiarise yourself with the preconceptions and standards
Crab has.

### Conventions & Naming
Crab enforces a strict naming convention. This is utilised to create
consistency between nodes regardless of the component which generated
them - which ultimately makes for a more familiar user experience as
well as easier debugging. The naming convention used follows this
structure:

```
TYPE_DESCRIPTION_COUNTER_SIDE
```

_TYPE_ and _SIDE_ are always upper case and _DESCRIPTION_ is always
upper camel case. _COUNTER_ is a number used to prevent name clashes.

Below is a list of names to give context to this convention:

```
CTL_Hip_1_MD
SKL_UpperLeg_1_RT
MATH_ArmTwistMultiplier_3_LF
```

The idea behind this convention is twofold. Firstly it creates a naming
form which is easily parsable and therefore makes it easy for anyone
to throw together quick selection scripts.

Secondly its a convention which strives to make it very clear at-a-glance
what something is, as each part stands out from the preceeding and following
parts.

```
Note: This naming convention ensures that the name of a node never
ends with a number. Therefore if you ever see a DAG node with a number
at the end it implies a build failure or bug with a component.
```

All the mark up for the _TYPE_ and _SIDE_ parts of a naming convention
are defined in the file ```crab.config```.

## Creating a Rig
When editing and building a Rig using crab there is an assumption that
there will only ever be one rig present in the scene. This is to ensure
stability during the build process and that all objects are named
consistently and reliably.

This does __not__ affect how many rigs your reference into a scene when
animating.

To create a rig, launch the _Creator_ tool using ```crab.creator.launch()```

By default you will not see any available components - as there is no rig
to add components to. Click the _New Rig_ button <img src="https://raw.githubusercontent.com/mikemalinowski/crab/master/crab/resources/new_button.png" alt="drawing" width="30"/> and you will be prompted
to give a name for your rig. The name is not of great importance and is
simply used for the naming of the main root node (which you can manually
edit if you need to).

Once the rig node is created the UI will auto-populate with all the
components available to you.


## Build the Skeleton

This process is probably where you will spend most of your time as
the skeleton creation process is where you get to decide what parts
your rig will be made up from as well as giving you the chance to
proportion your rig.

To create a skeletal component simply select a component from the
_component list_ and then click the _add_ <img src="https://raw.githubusercontent.com/mikemalinowski/crab/master/crab/resources/add_button.png" alt="drawing" width="30"/> button. This will generate
the given component as a child of whatever joint you currently have
selected. If you do not have anything selected the component will be
built as a root component.

### Location Component
It is highly recommended that you start all rigs with a Location
component. This is especially true if you plan to utilise your rig
in a game engine.

In most situations you will never skin to the Location bone, but it
acts as a root bone for the rest of your rig - ensuring you always
have a single root element.

The control rig element of this component also gives you a master
controller as well as a location controller - making it trivial to
place the rig for animation whilst setting the root location
independently.

### Component Options
Most components offer you options to tailor the component to your
specific needs. Options may include a name field - allowing you to
specify a descriptive name for the component, or it may allow you
to specify parameters such as number of twist bones in an arm etc.

You need to set the values of these options to your requirements
__before__ creating the component.

## Building the Rig

Once you have generated and placed some components you can trigger
a build of the rig. This is the process of asking Crab to generate
the control rig over the skeleton. As part of this process the skeleton
is tied to the control rig.

To trigger a rig build you can simply hit the _Build_ button <img src="https://raw.githubusercontent.com/mikemalinowski/crab/master/crab/resources/build_button.png" alt="drawing" width="30"/>. You will
then see the controls generated over the skeleton.

### Editing the Controls

The chances are that the control shapes will be either too small or
too large for your geometry. However you can go in and alter the CV's
of any controls and these control changes will be retained during each
rebuild of the rig.

You may put the rig back into an editable state at any time by clicking
the _Edit_ button <img src="https://raw.githubusercontent.com/mikemalinowski/crab/master/crab/resources/edit_button.png" alt="drawing" width="30"/>. When back in edit mode you're free to re-adjust the
proportion of your skeleton or add and remove components.

Clicking _Build_ when the rig is already built will simply place the rig
back into an editable state before re-building the rig.

## Behaviours

Behaviours are a layer on top of components. Components come with a
specific rule in that each component is of skeletal form, therefore
a component is always part of the deformation rig.

However, because each component is an encapsulated rigging element they
can never interact with other components beyond a child/parent relationship.

This limitation is not always ideal, and some useful rigging features
require a knowledge of multiple components. Examples might include
the addition of space switching attributes, a Pole Vector control for
an arm is a particulalry good example, as its useful to allow this
control to move in the space of the hand, shoulder, chest, hip or rig
root. This easily spans _at least_ three different components.

This is where behaviours come in. Instead of the component making potentially
incorrect assumptions about what other components exist the space switching
can be applied as a Behaviour.

This is because Behaviours are always generated __after__ all the components
are built. Behaviours are then built _in order_, meaning behaviours can
interact with the results of other behaviours generated before it.

### Building Behaviours

When you apply a behaviour to a Rig through the Crab UI, you're adding
a behaviour specification to the list of applied behaviours but the
actual behaviour itself will not be generated until you trigger
a build of the rig.

## Rig Overview

Rigs can very often be made up of many different components and behaviours,
and it is not always clear what is in a rig. You can use the __overview__
tab in the _Creator Ui_ to see a list of all the components as well as
all the behaviours.

This UI will also show you the options which were set at the time a
component was generated. The options for components are always read
only as it is assumed that the options play an important role in the
generation of the skeleton.

The options of a behaviour __can__ be changed through this UI, as the
behaviour does not exist other than when the rig is actually built.

<img src="https://raw.githubusercontent.com/mikemalinowski/crab/master/crab/resources/crab_overview_tab.png" alt="drawing"/>

## Rig Iteration

The main key of Crab is to allow rigs to be generated, animated, edited
tweaked and rebuilt. Therefore you can - at any stage - place the rig
in edit mode to adjust the bone placement etc.

In this regard a typical workflow might look like this:

```
New Rig -> Add Components -> Build Rig -> Add Behaviours -> Rebuild Rig -> Test/Animate -> Re-Edit -> Build
```

<br><br><br><br><br><br>
![alt text](https://raw.githubusercontent.com/mikemalinowski/crab/master/crab/resources/breaker.png)
# Crab Animation Tools

Whilst a rig makes it easier for an animator to deform a mesh, they can
be complex beasts which means there is a lot of benefit to having a
suite of animation tools to accompany it.

Crab does not offer a fully fleshed Animation Toolkit (but I can
highly recommend AnimBot!), but it does offer some utility functions
geared toward the animator to allow the animator to interact with
the rig quickly.

## Launching Crab Animation

You can launch __Crab:Animator__ using the following code (which you
can throw in a shelf if you wish)

```python
import crab;crab.animator.launch()
```

## The Crab Animation UI
The ui - at least for the moment - is a glorified list of tools. Selecting
a tool in the list will show any options that tool exposes. You can then
simply double click the tool to instigate it.

<img src="https://raw.githubusercontent.com/mikemalinowski/crab/master/crab/resources/crab_animator.png" alt="drawing"/>
<br>
Each tool offers different options based on what the tool does. This tool
is currently in its infancy and is therefore currently quite minimal.


<br><br><br><br><br><br>
![alt text](https://raw.githubusercontent.com/mikemalinowski/crab/master/crab/resources/breaker.png)
# Extending Crab

This part of the documentation is intended for those who are interested
in writing their own components, behaviours or tools or for anyone who
wants to edit the core of Crab.

## Plugin Architecture

Crab relies heavily on the _factories_ module, and therefore much of
the functionality of Crab is easy to extend and add to. Below you will
see an outline of each plugin type and where you can find examples of
any built-in plugins.

Its worth noting that you can place any additions you make in the crab
plugins directory, or you can specify a seperate location for your
custom components/behaviours/tools by setting the path to your extensions
in the environment variable named __CRAB_PLUGIN_PATHS__

### Component Plugin

The component plugin type allows you to add new skeletal components
to crab. To implement a new component in _crab_ you should inherit
from the Component class ```crab.Component```

The component class expects you to re-implement four methods:

#### \_\_init\_\_
Re-implementing this allows you to expose build options which can
be queried from within the component. The __Base Componnent__ class
implements the options property as an attribute dictionary and thus
can be added to using attributes as shown here:

```python
import crab

class ExampleComponent(crab.Component):
    
    identifier = 'Example'
    
    def __init__():
        super(ExampleComponent, self).__init__()

        self.options.myExampleOption = True
        self.options.anotherExampleOption = 123

```

In this example we expose two options - one a bool and another an int.
Any options which use native python types will be automatically displayed
within the UI.

#### create_skeleton

This method is where you should implement the code which generates
the skeletal structure. You're given the parent as an argument and
everything you build in this function should be part of a joint hierarchy
under the parent.

Further to this, you should mark your __component root joint__ as being
the root of the skeletal component. This allows Crab to understand where
your component begins and another component ends. This is shown in the
example below.

Equally you can tag your joints with labels allowing you to access them
easily when building the control rig.

Finally, whilst not a requirement it is good practice to select the
most relevent end joint of your component at the end. This makes it
convenient for the user when quickly creating many components.

Here we can see an example of this function being implemented.

```python

    def create_skeleton(self, parent):
        # -- Create a joint. Note that we use a crab method
        # -- to create the joint. This is not a requirement
        # -- but it will handle the naming and has some
        # -- convenient arguments (outlined further down in this
        # -- documentation).
        root_joint = crab.create.joint(
            description=self.options.description,
            side=self.options.side,
            parent=parent,
            match_to=parent,
        )

        # -- Define this joint as being the skeleton root for
        # -- this component
        self.define_skeleton_root(root_joint)

        # -- We'll tag this joint with a label so we can easily
        # -- find it from within the create_rig function.
        self.tag(
            target=root_joint,
            label='RootJoint'
        )

        # -- Select the tip joint
        pm.select(root_joint)

        return True
```


#### create_guide

This method is not required to be implemented, but can be implemented
if your component has requirements which cannot be compleetely fullfilled
by the skeletal hierarchy.

An example of where this function is particularly useful is when implementing
a leg component which contains foot roll features. Such features are
aided by guide markers allowing hte user to tweak the points of rotations
for the controls. The supporting 'guides' can be generated within this
function and read from within the __create_rig__ function.

TODO: Requires example


#### create_rig

This function is where youc an build the actual control rig. This function
gives you direct access to both the __skeletal_component__ as well as
the __guide_component__ as arguments:

```python

    def create_rig(self, parent, skeleton_component, guide_component):
        pass
```

When building a control rig there are some tasks which must be carried
out. Every joint in your skeletal must be 'bound' to an item in your
control rig. This is of crucial importance because someone may add
a component as a child of any joint, and therefore Crab needs to determine
which node in your rig is a correlating control rig parent.

This process is kept simple by the exposure of a method called __bind__.
When calling this function you have the option to create a constraint (parent)
between the control rig element and the skeletal element. Any overloaded
arguments are passed directly to the __parentConstraint__ call made
within the function (useful if you want to maintainOffset etc).

This example shows the mechanism allowing you to query the __skeletal
component__ and the __guide componet__ based on the tagging made within
the __create_skeleton__ example.

```python
    def create_rig(self, parent, skeleton_component, guide_component):

        # -- We're given the skeleton component instance, so we can
        # -- utilise the find method to find the joint we need to build
        # -- a control against
        root_joint = skeleton_component.find('RootJoint')[0]

        # -- Create a transform to use as a control. This method
        # -- is a convenience function which handles the name
        # -- generation as well as object transform matching and
        # -- shape creation.
        node = crab.create.control(
            description=self.options.description,
            side=self.options.side,
            parent=parent,
            match_to=root_joint,
            shape=self.options.shape,
            lock_list=self.options.lock,
            hide_list=self.options.hide,
        )

        # -- All joints should have a binding. The binding allows crab
        # -- to know what control parent to utilise when building skeletal
        # -- components.
        # -- The act of binding also constrains the skeleton joint to the
        # -- control
        self.bind(
            root_joint,
            node,
        )

        # -- Select our tip joint
        pm.select(node)
```

To summarise, a component __must__ implement the _create_skeleton_ and
_create_rig_ methods. It may __optionally__ implement the
__create_Guide__ method if your component requires it.

#### crab.create

In the examples above we saw some functions being used to create controls
and joints. _Crab_ offers a few convinence functions for the creation
of Maya nodes which aim to make repetative tasks easier.

##### crab.create.generic

This is a creation function capable of creating any Maya Node type ensuring
it conforms to the crab naming conventions outlined earlier. It also offers
functionality to match the nodes transform (if it has a transform) to a 
specified node or a given matrix. Generally put, this function wraps up some
of the common functionality which typically goes hand in hand with node
creation. This is shown in the example here:

```python
import crab

location_marker = crab.create.generic(
    node_type='transform',
    prefix=crab.config.MARKER,
    description='SomeLocation',
    side=crab.config.LEFT,
    parent=some_other_node,
    match_to=another_node_in_the_scene,
)
```

In this example we would be greating a simple transform node which would be
assigned the name ```MRK_SomeLocation_1_LF```. It would be placed as a child
of _some_other_node_ and matched in worldspace to _another_no_in_the_scene_.


##### crab.create.control

This function calls ```crab.create.generic``` under the hood but does so for
a specific hierarchy of prefixes. A _crab control_ is made up of a hierarchy
of four transforms:

    * crab.config.ORG
    * crab.config.ZERO
    * crab.config.OFFSET
    * crab.config.CONTROL

This list allows for behaviours to be bound to controls and offsets for tools
to utilise. When a _match_to_ argument is given the _ORG_ is the node to be
matched meaning all the other nodes by default will be zero'd. 

The other main difference with the control is that you can assign it a shape.
Shapes are stored as json data and can be found in the 'shapes' directory
within crab. Equally, if you want to use your own shapes you can place them
anywhere under paths defined by the __CRAB_PLUGIN_PATHS__ environment variable.

You can generate the shape files by selecting a transform with at least one
__NurbsCurve__ under it, then running the following code:

```python
import crab
import pymel.core as pm

crab.utils.shapes.write(pm.selected()[0], r'C:\my_shape.json')
```

### Behaviour Plugin

Behaviours can be thought of as rig modifiers run after all components are
built. They are exempt from any kind of hierarchy rules or conventions and
therefore perfectly suited for generating behaviour which crosses component
boundaries.

Good examples of behaviours are control modifiers which allow control rig
elements to move in spaces beyond their own components. 

As such, a behaviour has no skeletal element at all, instead the __crab rig__
retains a list of behaviours *assigned* to it and each behaviour is executed
once the rig components are generated. 

Because of their nature, behaviours typically expose more options than 
components, and those options typically expect the names of items within the
control rig to operate on.

Just like the Component, we can re-implement the \_\_init\_\_ method to define
and expose our options:


```python
import crab

class ExampleBehaviour(crab.Behaviour):
    
    identifier = 'Example Behaviour'
    
    def __init__(self):
        super(ExampleBehaviour, self).__init__()

        self.options.target = ''
        self.options.drive_this = ''
```

Beyond that we need only to implement the __apply__ method.

````python

    def apply(self):

        # -- Start by getting the objects as pymel objects
        target = pm.PyNode(self.options.target)
        drive_this = pm.PyNode(self.options.drive_this)
        
        pm.parentConstraint(target, drive_this)
````

This is a rather simplistic example, but it shows our exposure of two options
where we expect the names of the nodes we're interested in to be defined. Then
within our __apply__ method we're simply getting those two objects and constraining
them together.


### Rigging Tool Plugin

Crab hosts a *rig tools factory* which contains a series user facing tools which 
are useful when working with skeletons or control rigs. This include tools to
mirror joints or control shapes etc. 

All Rigging Tool plugins are exposed to the user from within the __Crab Creator 
UI__. As with the other plugin types outlined above you may specify options
within the \_\_init\_\_ and utilse those within the *run* method.

Here we see an example of a simple tool:

```python
import crab
import pymel.core as pm

# ------------------------------------------------------------------------------
class SkinConnect(crab.RigTool):

    identifier = 'Skin : (Dis)Connect'
    
    def __init__(self):
        super(SkinConnect, self).__init__()
        self.options.connect = True
        
    def run(self):
        for skin in pm.ls(type='skinCluster'):
            skin.moveJointsMode(self.options.connect)
```


### Animation Tool Plugin

An animation tool is very similar to the rigging tool, however it has
two main differences:

    * Animation tools are only ever exposed through the crab.animator tool and not the crab.creator tool.
    
    * Animation Tool plugins have a viability function to determine whether the tool can operate on a given node


The __crab.animator__ tool refreshes based on selection changes, the ui will 
prioritise any tools designed specifically for the nodes being selected and place
them at the top. 
 
This is particularly useful if for instance you write a suite of tools designed
to work with a particular component. In this way you can design your tools such
that they will not be visible unless  you have an element of your component
selected.

Here we see an example of an animation too


```python
import crab
import pymel.core as pm

class MoveByOne(crab.tools.AnimTool):
    """
    Keys alls the controls in the scene
    """
    identifier = 'Move By One'
    icon = 'path_to_icon'
    
    @classmethod
    def viable(cls, node):
        
        # -- Only return true if this node has the word 'Foo' in
        if 'Foo' in node.name():
            return cls.PRIORITY_SHOW
        return cls.DONT_SHOW
              
    def run(self):
        for node in pm.selected():
            node.translateX.set(node.translateX.get() + 1)
```

In this tool we're specifically only showing the user the tool if it satisfies
a particular requirement otherwise we ask it not to be displayed.

If we want our tool to always be visible we can just return ```cls.ALWAYS_SHOW```


### Building through Code

Whilst in most situation the UI will be used to create and generate rigs
its entirely possible to build new rigs, add components and instigate rig
builds directly through code. Therefore everything you can do in the ui 
you can also do in code directly. For instance to create a new rig...

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


# Compatibility

Crab has been tested on __Windows__ using __Maya 2019__.


# Contribute

If you would like to contribute thoughts, ideas, fixes or features please get in touch! mike@twisted.space


