import os
from .cleaning import cleaner_registry
from .table_description import load_file

class Curator():
    def __init__(self, sqlalchemy_engine, description_paths):
        if len(description_paths) == 0:
            raise "No description_paths provided"
        self.engine = sqlalchemy_engine
        self.table_registry = {} # This is a pretty crummy data structure

        for path in description_paths:
            description = load_file(path)
            self.table_registry[description.name] = description

    # WIP
    # def insert_dicts(self, table_name, data):
    #     cleaned_data = self.clean_dicts(table_name, data)
    #     engine.
    #     # TODO
    #     http://docs.sqlalchemy.org/en/latest/faq/performance.html#i-m-inserting-400-000-rows-with-the-orm-and-it-s-really-slow
    # def test_sqlalchemy_core(n=100000):
    #     init_sqlalchemy()
    #     t0 = time.time()
    #     engine.execute(
    #         Customer.__table__.insert(),
    #         [{"name": 'NAME ' + str(i)} for i in xrange(n)]
    #     )
    #     print(
    #         "SQLAlchemy Core: Total time for " + str(n) +
    #         " records " + str(time.time() - t0) + " secs")


    def clean_dicts(self, table_name, data):
        table_description = self.table_registry[table_name]
        headers = data[0].keys()
        header_map = {}

        for header in headers:
            column_desc = next(column for column in table_description.columns if column.name == header)
            if not column_desc.cleaner:
                continue
            cleaner_class_name, _, cleaner_key  = column_desc.cleaner.partition('.')
            header_map[header] = {
                'cleaner': cleaner_class_name,
                'cleaner_key': cleaner_key
            }

        records = []
        for raw_record in data:
            record = {}
            for header, value in raw_record.items():
                # No cleaner specified
                if not header in header_map:
                    record[header] = value
                    continue

                cleaner_info = header_map[header]
                cleaner_name = cleaner_info['cleaner']
                cleaner_key = cleaner_info['cleaner_key']

                cleaner_class = cleaner_registry.find(name=cleaner_name)
                cleaner_instance = cleaner_class()
                if cleaner_key:
                    record[header] = getattr(cleaner_instance, f'transform_{cleaner_key}')(raw_record)
                else:
                    record[header] = cleaner_instance.transform(value)
            records.append(record)
        return records
