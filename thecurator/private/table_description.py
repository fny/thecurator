"""
In case it isn't already clear by the namespace, this is a private API. Use it
at your own risk.
"""
import os
import jsonschema
import yaml
import sys
import importlib

here = os.path.dirname(__file__)

"""Schema for table descriptions"""
SCHEMA = yaml.load(
    open(os.path.join(here, '../table_description_schema.yml')))


class Registry():
    """
    Registry of all the table descriptions with conveneint lookup functions.
    """
    def __init__(self, description_paths):
        self.tables_by_name = {}
        for path in description_paths:
            description = load_file(path)
            self.tables_by_name[description['name']] = description

    def get_table(self, table_name):
        """Returns a dictionary with details for the given table name
        """
        try:
            return self.tables_by_name[table_name]
        except KeyError:
            tb = sys.exc_info()[2]
            raise LookupError(f'No table found with name {table_name}').with_traceback(tb)

    def get_column(self, table_name, column_name):
        """Returns a dictionary with details for the given table column
        """
        try:
            return self.get_table(table_name)['columns_by_name'][column_name]
        except KeyError:
            tb = sys.exc_info()[2]
            raise LookupError(
                f'No column found in table {table_name} with name {column_name}'
            ).with_traceback(tb)

    def get_transform(self, table_name, column_name):
        """Returns the transform function for a given table and column
        """
        column = self.get_column(table_name, column_name)
        return column.get('transform_fn')


def load_file(file_path):
    """
    Loads a table description from the given path as a dict.

    Note this adds the following keys to the dict:

     - `columns_by_name` which is a dict of the tables columns by keyed by name
     - `transform_fn` the function corresponding to a column's transform key
    """
    description = yaml.load(open(file_path))
    validate(description)
    columns = description['columns']
    columns_by_name = {}
    for column in columns:
        column_name = column['name']
        columns_by_name[column_name] = column
        if 'transform' in column:
            column['transform_fn'] = convert_transform_to_fn(column['transform'])
    description['columns_by_name'] = columns_by_name
    return description


def convert_transform_to_fn(transform_key):
    """
    Converts the value provided as a transformation key into a function by
    performing the required module lookup.

    For example, `transforms.numeric.absolute_value` would fetch the function
    `absolute_value` function from a `transforms.numeric` package.
    """
    split = transform_key.split('.')
    fn_name = split.pop()
    module_name = '.'.join(split)
    module = importlib.import_module(module_name)
    fn = getattr(module, fn_name)
    if fn is None:
        raise ValueError(f'No transform found for {transform_key}')
    return fn


def validate(table_description):
    """Ensures the provided table description is valid.

    Args:
        description (dict): Dictionary representation of the table description

    Returns:
        bool: whether the given description is valid.

    Raises:
        ValueError: When the provided description doesn't match the schema
    """
    return jsonschema.validate(table_description, SCHEMA)
