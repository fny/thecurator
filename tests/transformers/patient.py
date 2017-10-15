from thecurator import requires_row


@requires_row
def name(row):
    if age(row) > 50:
        return 'old'
    else:
        return 'young'


@requires_row
def age(row):
    return int(row['age'])
