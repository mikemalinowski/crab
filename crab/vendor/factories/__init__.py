"""
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
"""
factories is a module which exposes a take on the Factory/Plugin design 
pattern. The idea behind this pattern is to be able to define a structure 
which your functionality sits within - allowing you to call that 
functionality without ever really knowing what it is doing.

This approach is particularly useful when building systems which are 
likely to expand in unknown ways over time. Example use cases might include:

    * Toolboxes, where each tool is represented as a plugin - and an 
        interface which is arbitrarily populated with those tools

    * Node graphs, where we have no up-front knowledge of what nodes 
        may be available to use

    * Data parsers which include data that changes format over time due 
        to deprecation, meaning each data type can be represented by a 
        plugin allowing the framework to never care about the storage 
        details of the data

The commonality between all these structures is that the core of each 
system needs to do something but it does not have to care about the 
detail of how that task is achieved. Instead the detail is held within 
plugins libraries which can be expanded and contracted over time.

This pattern is incredibly useful but tends to come with an overhead 
of writing dynamic loading mechanisms and functionality to easily 
interact and query the plugins. The Factories module aims to diminish
that overhead - allowing you to focus on your end goal and the 
development of plugins.

This library was written based from the information here:
https://sourcemaking.com/design_patterns/factory_method

It is also designed based on the principals given during the
GDC 2018 Talk - A Practical Approach to Developing Forward-Facing Rigs, Tools and
Pipelines. Which can be explored in more detail here:
https://www.gdcvault.com/play/1025427/A-Practical-Approach-to-Developing
"""
__author__ = "Michael Malinowski"
__copyright__ = "Copyright (C) 2019 Michael Malinowski"
__license__ = "MIT"
__version__ = "1.2.0"

from .factory import (
    Factory,
)

from .constants import (
    log,
)
