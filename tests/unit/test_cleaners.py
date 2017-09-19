from thecurator.cleaning import BaseCleaner, CleanerFailure, CleanerRegistry
from fixtures.cleaners import DoNothingCleaner, ReturnDictCleaner, PositiveNumberCleaner, PatientCleaner, LabCleaner

class TestCleanerWithoutImplementation():
    def setup_method(self):
        self.cleaner = DoNothingCleaner()

    def test_transform_returns_given(self):
        value = 'whatever'
        assert self.cleaner.transform(value) == value

    def test_clean_returns_given(self):
        value = 'whatever'
        assert self.cleaner.clean(value) == value

    def test_clean_all(self):
        assert self.cleaner.clean_all([1, 2, 3]) == [1, 2, 3]


class TestPositiveNumberCleaner():
    def setup_method(self):
        self.cleaner = PositiveNumberCleaner()

    def test_unhandled_type(self):
        failure = self.cleaner.clean(10.1)
        assert type(failure) is CleanerFailure
        assert "returned None" in failure.message


class TestCleanerWithoutImplementation():
    def setup_method(self):
        self.cleaner = DoNothingCleaner()

    def test_transform_returns_given(self):
        value = 'whatever'
        assert self.cleaner.transform(value) == value

    def test_clean_returns_given(self):
        value = 'whatever'
        assert self.cleaner.clean(value) == value


class TestFailure():
    def test_behaves_falsey(self):
        failure = CleanerFailure('message', 'something', 'location')
        assert not failure


class TestPositiveNumberCleaner():
    def setup_method(self):
        self.cleaner = PositiveNumberCleaner()

    def test_unhandled_type(self):
        failure = self.cleaner.clean(10.1)
        assert type(failure) is CleanerFailure

class TestLabCleaner():
    """Tests for a dictionary returning cleaner."""
    def setup_method(self):
        self.cleaner = LabCleaner()

    def test_transformation_registry(self):
        assert LabCleaner.transformations == {
            'name': getattr(LabCleaner, 'transform_name'),
            'value': getattr(LabCleaner, 'transform_value')
        }

    def test_clean(self):
        result = self.cleaner.clean({'name': ' ALERTNESS ', 'value': 'high'})
        assert result == {'name': 'alertness', 'value': 2}
