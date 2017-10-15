import os
import jsonschema
import yaml
import sys
import importlib

script_path = os.path.dirname(__file__)

SCHEMA = yaml.load(
    open(os.path.join(script_path, './table_description/schema.yml')))


class Registry():
    def __init__(self, description_paths):
        self.tables_by_name = {}
        for path in description_paths:
            description = load_file(path)
            self.tables_by_name[description['name']] = description

    def get_table(self, table_name):
        try:
            return self.tables_by_name[table_name]
        except KeyError:
            tb = sys.exc_info()[2]
            raise LookupError(f'No table found with name {table_name}').with_traceback(tb)

    def get_column(self, table_name, column_name):
        try:
            return self.get_table(table_name)['columns_by_name'][column_name]
        except KeyError:
            tb = sys.exc_info()[2]
            raise LookupError(f'No column found in table {table_name} with name {column_name}').with_traceback(tb)

    def get_transform(self, table_name, column_name):
        column = self.get_column(table_name, column_name)
        return column.get('transform_fn')


def load_file(file_path):
    """TODO Description
    Args:
        file_path (str): Path to YAML description.

    Returns:
        addict.Dict
    """
    description = yaml.load(open(file_path))
    validate(description)
    columns = description['columns']
    columns_by_name = {}
    for column in columns:
        column_name = column['name']
        columns_by_name[column_name] = column
        if 'transform' in column:
            column['transform_fn'] = __convert_transform_to_fn(column['transform'])
    description['columns_by_name'] = columns_by_name
    return description


def __convert_transform_to_fn(transform_key):
    split = transform_key.split('.')
    fn_name = split.pop()
    module_name = '.'.join(split)
    module = importlib.import_module(module_name)
    fn = getattr(module, fn_name)
    if fn is None:
        raise ValueError(f'No transform found for {transform_key}')
    return fn


def validate(description):
    """Ensures the provided description is valid.

    Args:
        description (dict): Dictionary representation of the table description

    Returns:
        bool: whether the given description is valid.

    Raises:
        ValueError: When the provided description doesn't match the schema
    """
    return jsonschema.validate(description, SCHEMA)
