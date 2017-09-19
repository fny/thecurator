import os

import addict
import jinja2
import jsonschema
import yaml
import sqlalchemy
script_path = os.path.dirname(__file__)

SCHEMA = yaml.load(open(os.path.join(script_path, './table_description/schema.yml')))
TEMPLATE_PATH = os.path.join(script_path, './table_description/template.yml.jinja2')

def generate(sqlalchemy_engine, table_name, output_path=None):
    """Generates description file to fill out for the specified table"""

    if output_path and os.path.isfile(output_path):
        print("The file '{}' already exists!".format(output_path))
        return 1

    import jinja2

    jinja2.filters.FILTERS['map_type'] = __map_sqlalchemy_column_type
    template = jinja2.Template(open(TEMPLATE_PATH).read())

    inspector = sqlalchemy.engine.reflection.Inspector.from_engine(sqlalchemy_engine)
    output = template.render(columns = inspector.get_columns(table_name))

    if output_path:
        with open(output_path, 'w') as f:
            f.write(output)
        print("Description template for {}, written to {}".format(table_name, output_path))
    else:
        return output

def load_file(file_path):
    """Returns a and addict.Dict for the given provided table description.

    Args:
        file_path (str): Path to YAML description.

    Returns:
        addict.Dict
    """
    description = yaml.load(open(file_path))
    __validate(description)
    return addict.Dict(description)

def __map_sqlalchemy_column_type(sqlalchemy_column_type):
    """Map the SQLAlchemy column type to one for the description template"""
    if sqlalchemy_column_type is sqlalchemy.types.Integer:
        return 'integer'
    if sqlalchemy_column_type is sqlalchemy.types.Float:
        return 'decimal'
    if sqlalchemy_column_type is sqlalchemy.types.String:
        return 'string'
    if sqlalchemy_column_type is sqlalchemy.types.Date:
        return 'date'
    if sqlalchemy_column_type is sqlalchemy.types.DateTime:
        return 'datetime'
    raise "No mapping for SQLAlchemy column type {}".format(sqlalchemy_column_type)

def __validate(description):
    """Ensures the provided description is valid.

    Args:
        description (dict): Dictionary representation of the table description

    Returns:
        bool: whether the given description is valid.

    Raises:
        ValueError: When the provided description doesn't match the schema
    """
    return jsonschema.validate(description, SCHEMA)
