import inspect
import sqlalchemy
from .private import pypy_incompatible
from .private.table_description import Registry

"""Version number of this package"""
__VERSION__ = (0, 1, 4)


def requires_row(func):
    """Decorator used to mark transforms that require an entire row as input.

    Attributes:
        func (function): The function

    Returns:
        function: The function with an
    """
    func.requires_row = True
    return func


def transform_failure(self, message, raw_value, location=None):
    """Creates a TransformFailure used to detail when things go wrong.

    Attributes:
        message (string): The message you want to display
        raw_value (any): The value to be transformed
        location (string, optional): Source of the error, defaults to caller

    Returns:
        TransformFailure
    """
    caller = inspect.getframeinfo(inspect.stack()[1][0])
    if not location:
        location = "%s:%d" % (caller.filename, caller.lineno)
    return TransformFailure(message, raw_value, location)


class Curator():
    def __init__(self, sqlalchemy_engine, description_paths):
        """
        """
        if len(description_paths) == 0:
            raise ValueError("Description paths argument provided was empty")

        self.engine = sqlalchemy_engine
        self.sqlalchemy_meta = sqlalchemy.MetaData()
        self.sqlalchemy_meta.reflect(bind=sqlalchemy_engine)
        self.table_registry = Registry(description_paths)

    def insert_dicts(self, table_name, raw_rows):
        """Transform and insert the provided dicts into the database.

        Insertion occurs in a database transaction, so if any failure occurs
        an exception will be raised and nothing will be writtent to the
        database.

        Args:
            table_name (str): Message to incorporate into the final message
            raw_rows (dict): Value the failure occurred for

        Raises: Exception when the insert fails
        """
        cleaned_rows = self.transform_dicts(table_name, raw_rows)
        table = self.sqlalchemy_meta.tables[table_name]
        connection = self.engine.connect()
        transaction = connection.begin()
        try:
            connection.execute(table.insert(), cleaned_rows)
        except Exception:
            transaction.rollback()
            raise Exception('Insert failed')

    def transform_dicts(self, table_name, raw_rows):
        """Transforms dicts according to the table description.

        Args:
            table_name (str): Message to incorporate into the final message
            raw_rows (:obj:`list` of :obj:`dict`): Rows to transform

        Returns:
            :obj:`list` of :obj:`dict`: Transformed dicts
        """
        column_names = self.table_registry.get_table(table_name)['columns_by_name'].keys()
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

    @pypy_incompatible
    def transform_df(self, table_name, df):
        """Transforms a pandas.DataFrame in place according to the description.

        Args:
            table_name (str): Message to incorporate into the final message
            df (pandas.DataFrame): Value the failure occurred for

        Returns:
            pandas.DataFrame: In-place transformed DataFrame
        """
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
    transformation.

    Args:
        message (str): Message to incorporate into the final message
        value (any): Value the failure occurred for
        location (str): Where in the code the failure occurred

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
