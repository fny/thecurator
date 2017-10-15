import inspect
import sqlalchemy

from .table_description import Registry, load_file


__version__ = (0, 0, 2)


def requires_row(func):
    func.requires_row = True
    return func


def transform_failure(self, message, raw_value, location=None):
    caller = inspect.getframeinfo(inspect.stack()[1][0])
    if not location:
        location = "%s:%d" % (caller.filename, caller.lineno)
    return TransformFailure(message, raw_value, location)


class Curator():
    def __init__(self, sqlalchemy_engine, description_paths):
        if len(description_paths) == 0:
            raise ValueError("Description paths argument provided was empty")

        self.engine = sqlalchemy_engine
        self.sqlalchemy_meta = sqlalchemy.MetaData()
        self.sqlalchemy_meta.reflect(bind=sqlalchemy_engine)
        self.table_registry = Registry(description_paths)

    def insert_dicts(self, table_name, data):
        table = self.sqlalchemy_meta.tables[table_name]
        connection = self.engine.connect()
        transaction = connection.begin()
        try:
            cleaned_values = self.clean_dicts(table_name, data)
            connection.execute(table.insert(), cleaned_values)
        except:
            transaction.rollback()
            raise

    def clean_dicts(self, table_name, raw_rows):
        column_names = raw_rows[0].keys()
        transforms_by_column = {}
        for column_name in column_names:
            transforms_by_column[column_name] = \
                self.table_registry.get_transform(table_name, column_name)
        cooked_rows = []
        for raw_row in raw_rows:
            cooked_row = {}
            for column_name, raw_value in raw_row.items():
                transform = transforms_by_column[column_name]
                if not transform:
                    cooked_row[column_name] = raw_value
                elif hasattr(transform, 'requires_row'):
                    cooked_row[column_name] = transform(raw_row)
                else:
                    cooked_row[column_name] = transform(raw_value)
            cooked_rows.append(cooked_row)
        return cooked_rows

    def clean_df(self, table_name, df):
        for column_name in df.columns:
            transform = self.table_registry.get_transform(table_name, column_name)
            if not transform:
                continue
            elif hasattr(transform, 'requires_row'):
                df[column_name] = df.apply(transform, axis=1)
            else:
                df[column_name] = df[column_name].map(transform)
        return df


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
        return f'<thecurator.TransformFailure "{self.message}">'

    def __repr__(self):
        return self.__str__()
