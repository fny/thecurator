from thecurator import requires_row


@requires_row
def name(raw):
    raw_name = raw['name']
    return '_'.join(raw_name.strip().split()).lower()


@requires_row
def value(raw):
    cleaned_name = name(raw)
    value = raw['value'].lower()

    if cleaned_name == 'alertness':
        cleaned_value = {'low': 0, 'medium': 1, 'high': 2}[value]
        return cleaned_value
    else:
        return float(value)
