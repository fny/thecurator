import csv
import pandas
from helpers import relative_path, expand_path
from thecurator import Curator
from fixtures.db import engine
from fixtures.data.labs_clean import data as labs_clean


class FixtureData():
    def __init__(self, file_path):
        self.headers = None
        self.data = []
        fixture_path = relative_path(__file__, f'fixtures/data/{file_path}')
        with open(fixture_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for i, row in enumerate(csv_reader):
                if i == 0:
                    self.headers = row
                else:
                    self.data.append(row)

    def rows(self):
        """Returns the data as rows"""
        return self.data

    def columns(self):
        """Returns the data as columns"""
        column_data = [[] for _ in range(0, len(self.data[0]))]
        for row in self.data:
            for i, col in enumerate(row):
                column_data[i].append(col)
        return column_data

    def dicts(self):
        """Returns the data as dicts"""
        dict_data = []
        for row in self.data:
            bundle = dict(zip(self.headers, row))
            dict_data.append(bundle)
        return dict_data

    def df(self):
        return pandas.DataFrame(self.dicts())


class TestFixtureData():
    """Tests to make sure the fixture data helper above functions as we expect"""
    def setup_method(self):
        self.data = FixtureData('labs_dirty.csv')

    def test_headers(self):
        assert self.data.headers == ['patient_mrn', 'name', 'value', 'order_time', 'taken_time']

    def test_rows(self):
        assert self.data.rows()[0] == ['A', 'Blood Pressure', '120', '09/03/17 10:30AM', '09/03/17 11:30AM']

    def test_columns(self):
        assert self.data.columns()[0] == ['A', 'B', 'B', 'C', 'C', 'C']

    def test_dicts(self):
        assert self.data.dicts()[0] == {
            'patient_mrn': 'A',
            'name': 'Blood Pressure',
            'value': '120',
            'order_time': '09/03/17 10:30AM',
            'taken_time': '09/03/17 11:30AM'
        }


description_paths = expand_path(__file__, 'fixtures/descriptions/*.yml')
curator = Curator(engine, description_paths)


class TestCurator():
    def setup_method(self):
        self.labs_dirty = FixtureData('labs_dirty.csv')
        self.patients_dirty = FixtureData('patients_dirty.csv')

    def test_transform_dicts(self):
        results = curator.transform_dicts('lab', self.labs_dirty.dicts())
        for result, clean in zip(results, labs_clean):
            assert result == clean

    def test_transform_df(self):
        df = self.labs_dirty.df()
        results = curator.transform_df('lab', df)
        assert pandas.DataFrame(labs_clean).to_dict() == results.to_dict()

    def test_insert_dicts(self):
        curator.insert_dicts('lab', self.labs_dirty.dicts())
