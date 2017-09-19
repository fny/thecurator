import csv
import glob
import json
import os
from thecurator.curation import Curator
from fixtures.db import engine

def relative_path(path):
    return os.path.join(os.path.dirname(__file__), path)

class FixtureData():
    def __init__(self, file_path):
        self.headers = None
        self.data = []
        fixture_path = relative_path(f'../fixtures/data/{file_path}')
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
curator = Curator(engine, glob.glob(relative_path('../fixtures/descriptions/*.yml')))
labs_clean = json.loads(open(relative_path('../fixtures/data/labs_clean.json')).read())

class TestCurator():
    def setup_method(self):
        self.labs_dirty = FixtureData('labs_dirty.csv')
        self.patients_dirty = FixtureData('patients_dirty.csv')

    def test_clean_dicts(self):
        results = curator.clean_dicts('lab', self.labs_dirty.dicts())
        for result, clean in zip(results, labs_clean):
            assert result == clean

