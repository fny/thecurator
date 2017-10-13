import inspect


class TransformerRegistry():
    """Registry for all transformations.

    A transformer registry is used to search for transformers base on different
    parameters. For a typically application, you'd typically only have a
    singleton registry instance that's used across the application.
    """

    def __init__(self):
        self._registry = {}

    def add(self, transformer_class):
        """Adds the given class to the registry by name.

        Note transformers with the same class name will override one another.

        Example:
            >>> TransformerRegistry()
            >>> TransformerRegistry.add(AppleCleaner)
        """
        # Raises:
        #     ValueError: If a class provided isn't a transformer.
        # if not issubclass(klass, BaseCleaner):
        #     raise ValueError(f"{klass} isn't a subclass of BaseCleaner")
        self._registry[transformer_class.__name__] = transformer_class

    def transformers(self):
        """Returns the transformers stored in the registry."""
        return self._registry.values()

    def find(self, name=None):
        """Finds a transformer for the provided attributes.

        Note:
            The name is specified as a keyword argument to allow for
            additional filters to be added in future versions.

        Args:
            name (str): The name of the transformer class.

        Returns
            The transformer :obj:`class` if successful, None otherwise.
        """
        klass = self._registry[name]
        if not klass:
            return None
        return klass


"""Singleton registry of all transformers."""
transformer_registry = TransformerRegistry()


class BaseTransformer():
    """Base class for all transformers."""
    def __init_subclass__(cls, **kwargs):
        # TODO: Skip abstract classes
        transformer_registry.add(cls)

    def transform(self, raw_value):
        """Overridden method that transforms a dirty value into a clean value."""
        return raw_value

    def clean(self, raw_value):
        """Executes the transformation against the provided value, wrapping
        exceptions in TransformFailure.

        Returns:
            The value of the transformation or a TransformFailure in the case of
            an exception.
        """
        try:
            result = self.transform(raw_value)
            if result is TransformFailure:
                return result
            return result
        except Exception as e:
            return self._failure(e.__cause__, raw_value, e.__traceback__)

    def _failure(self, message, raw_value, location=None):
        caller = inspect.getframeinfo(inspect.stack()[1][0])
        if not location:
            location = "%s:%d" % (caller.filename, caller.lineno)
        return TransformFailure(message, raw_value, location)


class ValueTransformer(BaseTransformer):
    pass


def output(fn):
    """Marks a method as one to use for output. Used with NamedTransformer"""
    fn.output = True
    return fn


class OutputTracking(type):
    """Creates a dictionary of functions marked with `output = True`
    Those functions are marked by the `@output` decorator. After the dicionary
    is built, it's stored as the class attribute `outputs`.
    """
    def __new__(cls, name, bases, attr):
        marked = {}
        for obj in attr.values():
            if hasattr(obj, 'output'):
                marked[obj.__name__] = obj
        attr['outputs'] = marked
        return type.__new__(cls, name, bases, attr)


class NamedTransformer(BaseTransformer, metaclass=OutputTracking):
    @classmethod
    def has_transformation(cls, name):
        return name in cls.transformations

    def transform(self, raw_dict):
        """Returns a result dict using methods marked with @output"""
        result = {}

        for name, func in self.__class__.outputs.items():
            result[name] = func(self, raw_dict)
        return result


DICT_TRANSFORMER_PREFIX = 'transform_'


class DictTransformer(BaseTransformer):
    """Transformer that returns dicts based on methods with special prefixes.

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
            if name.startswith(DICT_TRANSFORMER_PREFIX):
                registry_name = name.replace(DICT_TRANSFORMER_PREFIX, '')
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


class TransformError(Exception):
    """Raised when a failure occurs while transforming a data element

    Args:
        failure (CleanerFailure): CleanerFailure to wrap display in the error

    Note:
        This implementation of this class is considered internal and is not
        considered stable for public use. While we guarantee you'll a
        TransformError will be raised when something goes wrong, we don't
        guarantee what the error will contain or how it's instantiated.
    """

    def __init__(self, failure):
        self.failure = failure
        super(TransformError, self).__init__(failure.message)


def failure(self, message, raw_value, location=None):
    caller = inspect.getframeinfo(inspect.stack()[1][0])
    if not location:
        location = "%s:%d" % (caller.filename, caller.lineno)
    return TransformFailure(message, raw_value, location)


class TransformFailure():
    """Returned by a transformer whenever something goes wrong during a
    transform call.

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
        return f'<thecurator.transformation.TransformFailure "{self.message}">'

    def __repr__(self):
        return self.__str__()


class BaseCleaner(BaseTransformer):
    """Alias for BaseTransformer"""
    pass


class DictCleaner(DictTransformer):
    """Alias for DictCleaner"""
    pass
