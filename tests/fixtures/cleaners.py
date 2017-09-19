from thecurator.cleaning import BaseCleaner, DictCleaner
import re
NUMBER_PATTERN = re.compile(r'[\d,]+')

class DoNothingCleaner(BaseCleaner):
    """Cleaner that returns given value"""
    def transform(self, raw):
        return raw

class ReturnDictCleaner(DictCleaner):
    """Returns the dict { 'one': 1, 'two': 2, 'three': 3} on transform"""
    def transform_one(self, raw):
        return 1

    def transform_two(self, raw):
        return 2

    def transform_three(self, raw):
        return 3

    def ignored(self, raw):
        return raw


class PositiveNumberCleaner(BaseCleaner):
    """Clean numbers and number like strings to ensure they're positive"""
    def transform(self, raw_value):
        if type(raw_value) is int:
            if value <= 0:
                return self._failure("Value should be positive", value)
            else:
                return value
        if type(raw_value) is str:
            if '-' in value:
                return self._failure("String looks negative", value)
            elif not NUMBER_PATTERN.match(value):
                return self._failure("Failed to match nubmer pattern.", value)
            else:
                return int(re.sub(',', '', value))
        return self._failure("Unsure how to handle value type", raw_value)

class PatientCleaner(DictCleaner):
    def transform_name(self, raw):
        age = self.transform_age(raw)
        if age > 50:
            return 'old'
        else:
            return 'young'

    def transform_age(self, raw):
        return int(raw)


class LabCleaner(DictCleaner):
    def transform_name(self, raw):
        raw_name = raw['name']
        return '_'.join(raw_name.strip().split()).lower()

    def transform_value(self, raw):
        name = self.transform_name(raw)
        value = raw['value'].lower()

        if name == 'alertness':
            cleaned_value = { 'low': 0, 'medium': 1, 'high': 2 }[value]
            return cleaned_value
        else:
            return float(value)

import dateparser

class DateTimeCleaner(BaseCleaner):
    def transform(self, value):
        return dateparser.parse(value).isoformat()
