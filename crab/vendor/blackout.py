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
blackout is a small micro-module which makes it easier to completely
forget packages. This is particularly useful when working with packages
made up of multiple sub-modules.

And example might be:

    /site-packages/foo/__init__.py
    /site-packages/foo/bar.py

If bar.py has a function called foo() within it, and we change that
function then it is not enough to reload foo, we must specifically
reload foo as well as foo.bar. 

When working with packages with any modules this can be time consuming
and problematic - particularly when developing within a host which is
persistent.

blackout helps, because we can unload the package in its entirety in 
a single line using:

    ```blackout.drop('foo')```

This will remove any hold to foo as well as any submodules of foo. In this 
case we can simply call ```import foo``` again, knowing that everything
within that package is being loaded fresh.
"""

import sys
import types


__author__ = "Michael Malinowski"
__copyright__ = "Copyright (C) 2019 Michael Malinowski"
__license__ = "MIT"
__version__ = "1.0.4"


# ------------------------------------------------------------------------------
def drop(package):
    """
    This will drop a package and all sub-packages from the sys.modules
    variable. 
    
    This means that the package and its submodules will be reloaded whenever
    you next import it. 
    
    Beware, this is incredibly useful for development when you're working
    with packages which contain sub-modules you're actively changing but this
    does not handle any prior references to those modules, therefore it is not
    code that should be utilised in release code.
    
    :param package: Name of the package to drop
    :type package: str
    
    :return: None
    """

    if isinstance(package, types.ModuleType):
        package = package.__name__

    for m in list(sys.modules.keys()):
        if m == package or m.startswith('%s.' % package):
            del sys.modules[m]
