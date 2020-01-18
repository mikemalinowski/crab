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
from .constants import log

import re
import os
import sys
import uuid
import inspect

# -- Our direct file loading depends on whether we're
# -- in python 2 or python 3. Therefore we wrap these
# -- imports in a try except
try:
    # noinspection PyUnresolvedReferences
    from importlib.machinery import SourceFileLoader
    _py_version = 3

except ImportError:
    import imp
    _py_version = 2


# ------------------------------------------------------------------------------
class Factory(object):
    """
    This is a simple 'getting started with factories' module. It offers a
    simple factory Mechanisms with a few basic features:

        * Recursive folder searching for plugins
        * Simple function call for accessing the plugin list

    This is typically enough to get started, but its worth noting that
    the following (generally quite useful nice-to-have) features are
    absent:

        * Ability to specify a plugin identifer
        * Ability to access a plugin by identifier
        * Removing plugins from the factory
        * Plugin sorted in user-defined priority

    Finally, some restrictions based on this factory:

        * Files containing plugins must not contain relative imports
        * Plugins must not be in the same file as the abstract

    Many of these restrictions or missing features are relatively straight
    forward to implement, but as a starting point to getting used to - or
    experimenting with the plugin/factory approach this should suffice.
    
    It is recommended that you explore the plugged.examples location to 
    see a variety of use cases. but a quick peek at a code example might
    look like this:
    
    .. code-block:: python
    
        >>> import os
        >>> import factories
        >>> 
        >>> # -- We import these for demonstration purposes. We will utilise
        >>> # -- the base class and the demonstration plugins
        >>> import factories.examples.reader
        >>> import factories.examples.reader.readers
        >>> 
        >>> # -- Instance a factory, giving the abstract (so the factory
        >>> # -- knows what it can store) along with a list of locations
        >>> # -- which should be used to search within.
        >>> factory = factories.Factory(
        ...     abstract=factories.examples.reader.ReaderPlugin,
        ...     paths=[
        ...         os.path.dirname(factories.examples.reader.readers.__file__),
        ...     ]
        ... )
        >>> 
        >>> # -- We can now get a list of all the plugin identifiers which have
        >>> # -- been loaded
        >>> print(factory.identifiers())
        >>> 
        >>> # -- Equally we can start to request specific plugin classes
        >>> json_reader = factory.request('JSONReader')
    """

    # -- These are loading mechanism enums
    GUESS = 0
    LOAD_SOURCE = 1
    IMPORTABLE = 2

    # -- Regex to test for any of the relevant python
    # -- file types
    _PY_CHECK = re.compile('([a-zA-Z].*)(\.py$|\.pyc$)')

    # --------------------------------------------------------------------------
    def __init__(self,
                 abstract,
                 paths=None,
                 plugin_identifier=None,
                 versioning_identifier=None,
                 envvar=None,
                 mechanism=0,
                 log_errors=True):
        """
        :param abstract: The abstract class to utilise when searching for
            plugins within the add_pathed plugin locations
        :type abstract: Class

        :param paths: List of paths which should immediately be searched
            for plugins. All paths should be absolute.
            Any paths given directly to the factory during the initialisation
            will utilise the guessing Mechanisms
        :type paths: list(str, str, ...)

        :param plugin_identifier: This is used to idenfify one type of plugin
            from another. By default the plugin class name is used, however
            you can specify the name of an attribute or method on the class to
            be queried for this also.
            The plugin identifier can be queried from the factory using the
            identifiers() call, or the request(plugin_identifier) call.
        :type plugin_identifier: str

        :param versioning_identifier: If given this allows plugins with the
            same identifier to be differentiated. This allows for a default
            behaviour of always retrieving the latest plugin whilst allowing
            for lower priority plugins to be retrievable on request.
            This should be the name of an attribute or method on the plugin
            which always evaluates to a float or integer.
        :type versioning_identifier: str

        :param envvar: Optional environment variable name. If defined this
            will be inspected and split by ; and registered as paths.
        :type envvar: str
        """
        # -- Store our incoming variables
        self._abstract = abstract
        self._identifier = plugin_identifier or '__name__'
        self._version = versioning_identifier

        # -- Store a list of plugins
        self._plugins = list()

        # -- Store whether we should immediately log errors
        self._log_errors = log_errors

        # -- Store all the paths we add_path regardless
        # -- of what plugins they hold. We use a dictionary
        # -- for this so we can store the Mechanisms for each
        # -- path too
        self._add_pathed_paths = dict()

        # -- Any paths we're giving during the init we should
        # -- add_path
        if paths and isinstance(paths, (list, tuple)):
            for path in paths:
                self.add_path(path, mechanism=mechanism)

        # -- Now register any paths defined by environment variable
        if envvar and envvar in os.environ:
            for path in os.environ[envvar].split(';'):
                self.add_path(path, mechanism=mechanism)

    # --------------------------------------------------------------------------
    def __repr__(self):
        return '[FACTORY - Identifier: %s, Plugin Count: %s]' % (
            self._identifier,
            len(self._plugins),
        )

    # --------------------------------------------------------------------------
    def _log(self, message, is_warning=False):
        """
        Internal logging logic to handle errors and warnings.

        :param message:
        :param is_warning:
        :return:
        """
        # -- All factory logs include the abstract so it can be
        # -- easily identified
        message = '(%s) %s' % (
            self._abstract.__name__,
            message,
        )

        # -- Wrap this in a try, because we never want to fail because
        # -- we cannot log a message for any reason.
        try:
            if is_warning and self._log_errors:
                log.warning(message)

            else:
                log.debug(message)

        except:
            pass

        # -- Log regardless if we're a warning and we're supposed
        # -- to log errors

    # --------------------------------------------------------------------------
    def _get_identifier(self, plugin):
        """
        Utilises the plugin identifier value to request the identifying
        name of the plugin.

        :param plugin: Plugin to take the name from

        :return: str
        """
        # -- Pull out the object from the plugin
        identifier = getattr(plugin, self._identifier)

        # -- If the identifier is callable, then it is a method
        # -- so we need to call it to get the actual identifier
        if inspect.ismethod(identifier):
            return identifier()

        return identifier

    # --------------------------------------------------------------------------
    def _get_version(self, plugin):
        """
        Utilises the plugin version identifier value to request the version
        number of the plugin.

        :param plugin: Plugin to take the version from

        :return: int or float
        """

        # -- Pull out the object from the plugin
        identifier = getattr(plugin, self._version)

        # -- If the identifier is callable, then it is a method
        # -- so we need to call it to get the actual identifier
        if inspect.ismethod(identifier):
            return identifier()

        return identifier

    # --------------------------------------------------------------------------
    def _mechanism_load(self, filepath):
        """
        Attemps to find any plugins on the given filepath using the loading
        Mechanisms. This utilises import.load_source.

        As such, loading plugins through this Mechanisms has limitations in
        terms of not being able to utilise relative imports but it has the
        advantage of being able to load plugins from locations outside of
        the sys.path.

        :param filepath: Absolute filepath to the file to inspect
        :type filepath: str

        :return: List of found plugins
        """
        filename = os.path.splitext(
            os.path.basename(
                filepath,
            ),
        )[0]

        # -- Generate a unique name for the module to prevent
        # -- us from creating any clashes
        module_name = filename + str(uuid.uuid4())

        # -- The mechanism to load module files directly is specifically
        # -- different between python2 and python3, so we need to deal
        # -- with both cases.
        try:
            if _py_version == 3:
                return SourceFileLoader(
                    module_name,
                    filepath,
                ).load_module()

            elif _py_version == 2:
                if filepath.endswith('.py'):
                    return imp.load_source(
                        filename + str(uuid.uuid4()),
                        filepath,
                    )

                elif filepath.endswith('.pyc'):
                    return imp.load_compiled(
                        filename + str(uuid.uuid4()),
                        filepath,
                    )

        except BaseException:
            self._log(
                'Failed trying to direct load : %s (%s)' % (
                    filepath,
                    str(sys.exc_info()),
                ),
            )
            return None

    # --------------------------------------------------------------------------
    def _mechanism_import(self, filepath):
        """
        Attemps to resolve a pre-existing package from the given file. If
        the package is found it is returned otherwise we return None.

        :param filepath: Absolute filepath to access
        :type filepath: str

        :return: List of found plugins
        """
        # -- Attempt to get the module name. This will return None
        # -- if the module does not exist
        module_name = self._module_address(filepath)

        # -- If the module name exists in the sys.modules list
        # -- we return that module
        if module_name:
            self._log('Found Module : %s' % module_name)
            return sys.modules[module_name]

        # -- To get here the module is invalid or does not exist
        # -- so we return None
        return None

    # --------------------------------------------------------------------------
    @classmethod
    def _module_address(cls, filepath):
        """
        This will take a file and attempt to build up a module address from
        it by looking at the __init__ files around it.

        The module address will only be returned if it is successfully
        validated in the sys.modules. If no address could be determined this
        will return None.

        :param filepath: Filepath to attempt to resolve
        :type filepath: str

        :return:
        """
        # -- Ensure we're working with consistent character
        # -- types in the path
        filepath = filepath.replace('\\', '/')
        if 'unpacka' in filepath:
            pass

        # -- Do an immediate test to check if this is a lone-python
        # -- package
        lone_name = os.path.splitext(
            os.path.basename(filepath),
        )[0]

        # noinspection PyBroadException
        try:
            exec('import %s' % lone_name)

        except BaseException:
            pass

        # -- If the lone name is in the sys.modules list we then
        # -- need to check if it equates to the same file we're
        # -- looking at.
        if lone_name in sys.modules:
            add_pathed_path = sys.modules[lone_name].__file__.replace('\\', '/')

            # -- If it matches we return it as we do not need to start
            # -- looking at __init__ structures
            if filepath == add_pathed_path:
                return lone_name

        # -- Collage a list of parts which we can move between
        parts = filepath.split('/')
        package_parts = []

        # -- Keep cycling for as long as we have a path to actually
        # -- cycle
        while parts:

            # -- Build a path to look for
            # -- TODO: This needs to work with PYC & PYD files
            package_test = os.path.join(
                '/'.join(parts[:-1]),
                '__init__.py',
            )

            # -- Get the current part
            part = parts.pop()

            # -- If the path does not exist, we have hit the end
            # -- of the package
            if not os.path.exists(package_test):

                # -- Pop the final component and define the
                # -- sys path and the package name
                package_parts.append(part)
                package_name = '.'.join(reversed(package_parts))

                # -- If our package name has a suffix we need to remove
                # -- it. Note: We do not test the last characters, as
                # -- this means the test works for .py, .pyc and .pyd files
                if '.py' in package_name:
                    package_name = os.path.splitext(package_name)[0]

                # noinspection PyBroadException
                try:
                    exec('import %s' % package_name)

                except BaseException:
                    pass

                # -- Return our type of data
                if package_name in sys.modules:
                    return package_name

            # -- Pop the item and keep searching
            package_parts.append(part)

        # -- We could not determine the package name, so we
        # -- skip out
        return None

    # --------------------------------------------------------------------------
    def clear(self):
        """
        Clears the entire factory of plugins and add_pathed paths.

        :return: None

        ..code-block:: python

        >>> from factories.examples.reader import DataReader
        >>>
        >>> # -- Instance a new factory
        >>> reader = DataReader()
        >>>
        >>> # -- Print how many plugins we have
        >>> print(len(reader.factory.plugins()))
        2
        >>>
        >>> # -- Clear the factory
        >>> reader.factory.clear()
        >>>
        >>> # -- We now have no plugins in the factory
        >>> print(len(reader.factory.plugins()))
        0
        """
        # -- Start clearing out the factory variables
        self._plugins = list()
        self._add_pathed_paths = dict()

    # --------------------------------------------------------------------------
    def identifiers(self):
        """
        Returns a list of plugin class names add_pathed within the factory.

        The list of class names will be unique - therefore classes which share
        the same name will not appear twice.

        :return: list(str, str, ...)

        ..code-block:: python

            >>> from factories.examples.reader import DataReader
            >>>
            >>> # -- Instance a new factory
            >>> reader = DataReader()
            >>>
            >>> # -- Print how many plugins we have
            >>> print(reader.factory.identifiers())
            set(['JSONReader', 'INIReader'])
        """
        return {
            self._get_identifier(plugin)
            for plugin in self._plugins
        }

    # --------------------------------------------------------------------------
    def paths(self):
        """
        Returns all the paths add_pathed in the factory

        :return: List of paths

        ..code-block:: python

            >>> from factories.examples.reader import DataReader
            >>>
            >>> # -- Instance a new factory
            >>> reader = DataReader()
            >>>
            >>> # -- Print how many plugins we have
            >>> print(reader.factory.paths())
            {...factories/examples/reader/readers}
        """
        # -- Cast the keys to a list to ensure compatibility
        # -- between python 2.x and 3.x
        return list(self._add_pathed_paths.keys())

    # --------------------------------------------------------------------------
    def plugins(self):
        """
        Returns a unique list of plugins. Where multiple versions are available
        the highest version will be given.

        :return: list(class, class, ...)

        ..code-block:: python

            >>> from factories.examples.reader import DataReader
            >>>
            >>> # -- Instance a new factory
            >>> reader = DataReader()
            >>>
            >>> # -- Print how many plugins we have
            >>> for plugin in reader.factory.plugins():
            ...     print(plugin.__name__)
            JSONReader
            INIReader
        """
        return [
            self.request(identifier)
            for identifier in self.identifiers()
        ]

    # --------------------------------------------------------------------------
    # noinspection PyBroadException
    def add_path(self, path, mechanism=0):
        """
        Registers a search address with the factory. The factory will
        immediately being searching recursively within this location for
        any plugins.

        :param path: Absolute folder location
        :type path: str

        :param mechanism: This allows you to specify the behaviour for
            loading plugin. Current options are:

                * IMPORTABLE:
                    This mechanism should be used if your code resides within
                    already importable locations. This method is mandatory if
                    your code contains relative imports. Because this is
                    importing modules which are available on the sys.path the
                    class names will resolve nicely too.

                * LOAD_SOURCE
                    This is useful when your plugin code is outside of the
                    interpreters sys.path. This mechanism will load the file
                    directly rather than import it from sys.modules.
                    This method has flexibility in terms of structure but
                    means you cannot utilise relative import paths within
                    your plugin. All loaded plugins using this module are
                    imported into a namespace defined through a uuid.

                * GUESS
                    This is the default mechanism. When guessing the factory
                    will attempt to utilise the IMPORTABLE method first, and
                    only if the module is not accessible from within
                    sys.modules will it fall back to LOAD_SOURCE. This method
                    means you do not have to care too much, and is default
                    behaviour.
        :type mechanism: int

        :return: Count of plugins add_pathed

        ..code-block:: python

            >>> import os
            >>> import factories
            >>>
            >>> # -- We import these for demonstration purposes. We will utilise
            >>> # -- the base class and the demonstration plugins
            >>> import factories.examples.reader
            >>> import factories.examples.reader.readers
            >>>
            >>> # -- Instance a factory, giving the abstract (so the factory
            >>> # -- knows what it can store)
            >>> factory = factories.Factory(
            ...     abstract = factories.examples.reader.ReaderPlugin,
            ... )
            >>>
            >>> # -- Register a path, allowing the factory to guess whether
            >>> # -- to import or do a direct load
            >>> factory.add_path(
            ...     os.path.dirname(factories.examples.reader.readers.__file__),
            ...     mechanism=factory.GUESS,
            ... )
        """

        # -- Refuse none-type paths
        if not path:
            return 0

        # -- Regardless of what is found along the path we store the
        # -- fact that this path has been given to us
        self._add_pathed_paths[path] = mechanism

        # -- We return how many plugins have been add_pathed
        # -- by this path, so we get the plugin count prior
        # -- to doing anything
        current_plugin_count = len(self._plugins)

        filepaths = list()

        # -- Collate all our valid files in an initial pass. This could
        # -- be done in situ, but for the sake of clarity its done up-front
        for root, _, files in os.walk(path):
            for filename in files:

                # -- skip any private or structural files, along with
                # -- any files which are not py files
                if not self._PY_CHECK.match(filename):
                    continue

                filepaths.append(
                    os.path.join(
                        root,
                        filename
                    ),
                )

        # -- Start cycling over the files we have found and look inside
        # -- for plugins
        for filepath in filepaths:

            # -- Declare the variable we will ultimately inspect
            # -- for plugins
            module_to_inspect = None

            # -- If we need to import - or guess, then we attempt to
            # -- get the package name
            if mechanism == self.IMPORTABLE or mechanism == self.GUESS:
                module_to_inspect = self._mechanism_import(filepath)

                if module_to_inspect:
                    self._log('Module Import : %s' % filepath)

            # -- If we do not have a module, and we're using the loading
            # -- or guess Mechanisms
            if not module_to_inspect:
                if mechanism == self.LOAD_SOURCE or mechanism == self.GUESS:
                    module_to_inspect = self._mechanism_load(filepath)
                    if module_to_inspect:
                        self._log('Direct Load : %s' % filepath)

            # -- If the module is invalid for any reason we do not
            # -- go further
            if not module_to_inspect:
                self._log(
                    'Could not import or load : %s\n\t%s' % (
                        filepath,
                        str(sys.exc_info()),
                    ),
                    is_warning=True,
                )
                continue

            # -- We have no control over what we load, so we wrap
            # -- this is a try/except
            try:

                # -- Look for implementations of the abstract
                for item_name in dir(module_to_inspect):

                    item = getattr(
                        module_to_inspect,
                        item_name,
                    )

                    # -- If this bases off the abstract, we should store it
                    if inspect.isclass(item):

                        # -- We do not want to pick up the abstract
                        # -- itself, so ignore that
                        if item == self._abstract:
                            continue

                        if issubclass(item, self._abstract):
                            self._plugins.append(item)
                            self._log('Loaded Plugin : %s' % item)

            # -- We keep the exception type explitely broad as it
            # -- is completely out of our control what might be being
            # -- imported
            except BaseException:
                self._log(str(sys.exc_info()), is_warning=True)

        # -- Return the amount of plugins which have
        # -- been loaded during this registration pass
        return len(self._plugins) - current_plugin_count

    # --------------------------------------------------------------------------
    def register(self, class_type):
        """
        Registers the given class type as a plugin for this factory. Note,
        the class type being given must be inherited from the abstract.

        This is particularly useful if you have direct access to the plugin
        classes without needing to search disk locations.

        :param class_type: The class type to add into the factories
            repertoire
        :type class_type: type

        :return: True if the registration was successful.
        """
        if not inspect.isclass(class_type):
            return False

        if not issubclass(class_type, self._abstract):
            return False

        self._plugins.append(class_type)

    # --------------------------------------------------------------------------
    def reload(self):
        """
        This will forget any add_pathed plugins or information about plugins
        and perform a search over all the stored paths.

        :return:
        """
        # -- Take a snapshot of the path data
        path_data = self._add_pathed_paths.copy()

        # -- Start clearing out the factory variables
        self.clear()

        # -- Now cycle over the path data and re-add_path them
        for path, mechanism in path_data.items():
            self.add_path(
                path=path,
                mechanism=mechanism,
            )

    # --------------------------------------------------------------------------
    def request(self, plugin_identifier, version=None):
        """
        Retrieves the plugin with the specified plugin identifier. If you
        require a specific version of a plugin (in a scenario where there
        are multiple plugins with the same identifier) this can also be
        specified.

        :param plugin_identifier: The identifying value of the plugin you
            want to request
        :type plugin_identifier: str

        :param version: The version of the plugin you want. By default this
            is None. If the factory does not have a versioning identifier
            declared this argument has no affect.
        :type version: int

        :return: Plugin Class (or None)

        ..code-block::

            >>> from factories.examples.reader import DataReader
            >>>
            >>> # -- Instance a reader
            >>> reader = DataReader()
            >>>
            >>> # -- Get a plugin by identifier
            >>> plugin = reader.factory.request('JSONReader')
            >>>
            >>> print(plugin.__name__)
            JSONReader

        Equaly you can specify the version of a plugin you want when
        you're dealing with factories which have the version identifier
        defined:

        ..code-block:: python

            >>> from factories.examples.reader import DataReader
            >>>
            >>> # -- Instance a reader
            >>> reader = DataReader()
            >>>
            >>> # -- Get a plugin by identifier
            >>> plugin = reader.factory.request('JSONReader', version=1)
            >>>
            >>> print(plugin.__name__)
            JSONReader
            >>> print(plugin.version)
            1
        """
        # -- Get all the plugins which match the given
        # -- identifier
        matching_plugins = [
            plugin
            for plugin in self._plugins
            if self._get_identifier(plugin) == plugin_identifier
        ]

        # -- If there are no matching plugins we have nothing
        # -- to return
        if not matching_plugins:
            self._log(
                'No plugin matching %s' % plugin_identifier,
                is_warning=True,
            )
            return None

        # -- If we have not been given a versioning identifier
        # -- then we arbitrarily return from our matching plugins.
        if not self._version:
            return matching_plugins[0]

        # -- Sort out plugins in version order
        versions = {
            self._get_version(plugin): plugin
            for plugin in matching_plugins
        }

        # -- If we have not been given a version we simply return
        # -- the plugin with the highest value
        if not version:
            return versions[max(versions.keys())]

        # -- If the requested version is not in the versions
        # -- available we return None
        if version not in versions:
            self._log(
                'Version %s of %s could not be found' % (
                    version,
                    plugin_identifier,
                ),
                is_warning=True,
            )
            return None

        # -- Finally we return the requested version
        return versions[version]

    # --------------------------------------------------------------------------
    def remove_path(self, path):
        """
        This will remove a path from the path list. Any plugins from this 
        location will be removed.
        
        Note: This action performs a factory clear and re-scan.
        
        :param path: Path to remove from the factory. This must be an 
            absolute path
        :type path: str
        
        :return: None 
        
        ..code-block::
        
            >>> from factories.examples.reader import DataReader
            >>> 
            >>> # -- Instance a reader
            >>> reader = DataReader()
            >>> 
            >>> # -- Print the fact that we have two plugins
            >>> print(len(reader.factory.plugins()))
            2
            >>> # -- Unadd_path all our paths
            >>> for path in reader.factory.paths():
            ...     reader.factory.remove_path(path)
            >>> 
            >>> # -- We now have no plugins - as remove_pathing a path
            >>> # -- remove_paths the plugins too
            >>> print(len(reader.factory.plugins()))
            0
        """
        # -- Take a snapshot of the path data
        path_data = self._add_pathed_paths.copy()

        # -- Start clearing out the factory variables
        self._plugins = list()
        self._add_pathed_paths = dict()

        # -- Now cycle over the path data and re-add_path them
        for original_path, mechanism in path_data.items():

            # -- Skip the path we're being asked to remove
            if os.path.abspath(original_path) == os.path.abspath(path):
                continue

            self.add_path(
                path=original_path,
                mechanism=mechanism,
            )

    # --------------------------------------------------------------------------
    def versions(self, identifier):
        """
        Returns a list of all the versions available for the plugins with the
        given identifier. 
        
        :param identifier: Plugin identifier to check
        :type identifier: str
        
        :return: list(int, int, ...) 
        
        ..code-block:: python
        
            >>> from factories.examples.reader import DataReader
            >>> 
            >>> # -- Instance a reader
            >>> reader = DataReader()
            >>> 
            >>> # -- Get a plugin by identifier
            >>> print(reader.factory.versions('JSONReader'))
            [1]
        """
        if not self._version:
            return list()

        return sorted(
            self._get_version(plugin)
            for plugin in self._plugins
            if self._get_identifier(plugin) == identifier
        )
