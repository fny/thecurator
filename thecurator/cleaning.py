import sqlalchemy
import inspect
from abc import ABCMeta, abstractmethod


class CleanerRegistry():
    """Registry for all cleaners.

    A cleaner registry is used to search for cleaners base on different
    parameters. For a typically application, you'd typically only have a
    singleton registry instance that's used across the application.
    """
    def __init__(self):
        self._registry = {}

    def add(self, cleaner_class):
        """Adds an additional to the registry.

        Note that cleaners with the same class name will override one another.

        Example:
            >>> Registry()
            >>> Registry.add(AppleCleaner)
        """
        # Raises:
        #     ValueError: If a class provided isn't a cleaner.
        # if not issubclass(klass, BaseCleaner):
        #     raise ValueError(f"{klass} isn't a subclass of BaseCleaner")
        self._registry[cleaner_class.__name__] = cleaner_class


    def cleaners(self):
        """Returns the cleaners stored in the registry."""
        return self._registry.values()

    def find(self, name = None):
        """Finds a cleaner for the provided attributes.

        Note:
            The name is specified as a keyword argument to allow for
            additional filters to be added in future versions.

        Args:
            name (str): The name of the cleaner class.

        Returns
            The cleaner :obj:`class` if successful, None otherwise.
        """
        klass = self._registry[name]
        if not klass:
            return None
        return klass

"""Singleton registry of all cleaners."""
cleaner_registry = CleanerRegistry()

class BaseCleaner():
    """Base class for all cleaners."""
    __metaclass__ = ABCMeta

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not inspect.isabstract(cls): # Skip abstract classes
            cleaner_registry.add(cls)

    def clean(self, raw_value):
        """Executes the transformation against the provided value, wrapping exceptions in CleanerFailure.

        Returns:
            The value of the transformation or a CleanerFailure in the case of an exception.
        """
        try:
            result = self.transform(raw_value)

            if result is CleanerFailure:
                return result
            return result
        except Exception as e:
            return self._failure(e.__cause__, raw_value, e.__traceback__)

    @abstractmethod
    def transform(self, raw_value):
        """Overridden method that transforms a dirty value into a clean value."""
        pass

    def _failure(self, message, raw_value, location = None):
        caller = inspect.getframeinfo(inspect.stack()[1][0])
        if not location:
            location = "%s:%d" % (caller.filename, caller.lineno)
        return CleanerFailure(message, raw_value, location)

TRANSFORMER_PREFIX = 'transform_'

class DictCleaner(BaseCleaner):
    """Cleaner that returns dicts based on methods with special prefixes.

    Example:

        >>> class ExampleDictCleaner(DictCleaner):
        ...     def transform_one(self, value):
        ...         return 1
        ...     def transform_two(self, value):
        ...         return 2
        ...     def ignored():
        ...         return None

        >>> ExampleDictCleaner.transformations # doctest: +ELLIPSIS
        {
            'name': <function DictCleaner.transform_name at 0x...>,
            'value': <function MedicationCleaner.transform_value at 0x...>
        }

        >>> ExampleDictCleaner().clean(0)
        { 'one': 1, 'two': 2 }

    Attributes:
        transformations (dict): transformation functions to their key in the
            object returned by transform
    """
    __metaclass__ = ABCMeta

    def __init_subclass__(cls, **kwargs):
        """Tracks all methods added on init
        """
        # Call for Base Cleaner too!
        super().__init_subclass__(**kwargs)

        # Mapping of transformer names to transformer functions
        cls.transformations = {}

        for name, func in vars(cls).items():
            # Add all functions starting with the `TRANSFORMATION_PREFIX` to the
            # transformation registry
            if name.startswith(TRANSFORMER_PREFIX):
                registry_name = name.replace(TRANSFORMER_PREFIX, '')
                cls.transformations[registry_name] = func

    @classmethod
    def has_transformation(cls, name):
        return name in cls.transformations

    def transform(self, raw_dict):
        """Returns a dict based on the defined `transform_*` functions."""
        result = {}
        for name, func in self.__class__.transformations.items():
            result[name] = func(self, raw_dict)
        return result

class CleanerError(Exception):
    """Raised when a failure occurs while cleaning a data element

    Args:
        failure (CleanerFailure): CleanerFailure to wrap display in the error

    Note:
        This implementation of this class is considered internal and is not
        considered stable for public use. While we guarantee you'll be CleanerErrors
        will be raised when something goes wrong, we don't won't what the error
        will contain or how it's instantiated.
    """
    def __init__(self, failure):
        self.failure = failure
        super(CleanerError, self).__init__(failure.message)

class CleanerFailure():
    """Returned by a cleaner whenever something goes wrong.

    Args:
        message (str): Message to incorporate into the final message
        value: Value the failure occurred for
        location: Where in the code the failure occurred

    Note:
        This implementation of this class is considered internal and is not
        considered stable for public use. While we guarantee you'll be returned
        failures when something goes wrong, we don't won't what the failure
        will contain or how it's instantiated.

    Attributes:
        message (str): Message detailing what occur
    """
    def __init__(self, message, value, location):
        self.message = f"{message} (value: {repr(value)}) at {location}"
        self.value = value
        self.location = location

    def __bool__(self):
        """Makes failures falsey"""
        return False

    def __str__(self):
        return f'<thecurator.cleaning.CleanerFailure "{self.message}">'

    def __repr__(self):
        return self.__str__()
