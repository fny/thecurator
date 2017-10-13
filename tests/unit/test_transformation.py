from thecurator.transformation import TransformFailure
from fixtures.transformers import (DoNothingTransformer, ReturnDictTransformer,
                                   PositiveNumberCleaner, LabCleaner)


class TestReturnDictTransformer():
    def test_transform_returns_fixed_dict(self):
        result = ReturnDictTransformer().transform('whatever')
        assert result == {'one': 1, 'two': 2, 'three': 3}

    def test_clean_returns_fixed_dict(self):
        result = ReturnDictTransformer().clean('whatever')
        assert result == {'one': 1, 'two': 2, 'three': 3}


class TestTransformerWithoutImplementation():
    def setup_method(self):
        self.cleaner = DoNothingTransformer()

    def test_transform_returns_given(self):
        value = 'whatever'
        assert self.cleaner.transform(value) == value

    def test_clean_returns_given(self):
        value = 'whatever'
        assert self.cleaner.clean(value) == value


class TestFailure():
    def test_behaves_falsey(self):
        failure = TransformFailure('message', 'something', 'location')
        assert not failure


class TestPositiveNumberCleaner():
    def setup_method(self):
        self.cleaner = PositiveNumberCleaner()

    def test_unhandled_type(self):
        failure = self.cleaner.clean(10.1)
        assert type(failure) is TransformFailure


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
