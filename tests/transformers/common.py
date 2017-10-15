from thecurator import transform_failure
import dateparser
import re


NUMBER_PATTERN = re.compile(r'[\d,]+')


def positive_integer(raw_value):
    if type(raw_value) is int:
        if raw_value <= 0:
            return transform_failure("Value should be positive", raw_value)
        else:
            return raw_value
    if type(raw_value) is str:
        if '-' in raw_value:
            return transform_failure("String looks negative", raw_value)
        elif not NUMBER_PATTERN.match(raw_value):
            return transform_failure("Failed to match pattern.", raw_value)
        else:
            return int(re.sub(',', '', raw_value))
    return transform_failure("Unsure how to handle value type", raw_value)


def datetime(raw_value):
    return dateparser.parse(raw_value)


def strip(raw_value):
    return raw_value.strip()
