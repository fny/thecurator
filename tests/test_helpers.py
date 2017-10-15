"""Tests for helpers used in the tests"""
import helpers


def test_expand_path_simple_glob():
    read_values = []
    for path in helpers.expand_path(__file__, 'fixtures/glob/*.txt'):
        read_values.append(open(path).read())
    assert set(read_values) == set(['1\n', '2\n', '3\n'])


def test_expand_path_nested_glob():
    read_values = []
    for path in helpers.expand_path(__file__, 'fixtures/glob/**/*.txt'):
        read_values.append(open(path).read())
    assert set(read_values) == set(['A\n', 'B\n', 'C\n', 'D\n'])


def test_expand_path_with_single_path():
    expected = helpers.expand_path(__file__, 'fixtures/glob/*.txt')
    actual = helpers.expand_paths(__file__, 'fixtures/glob/*.txt')
    assert actual == expected


def test_expand_paths():
    read_values = []
    globs = ['fixtures/glob/*.txt', 'fixtures/glob/**/*.txt']
    for path in helpers.expand_paths(__file__, globs):
        read_values.append(open(path).read())
    assert set(read_values) == set(
        ['1\n', '2\n', '3\n', 'A\n', 'B\n', 'C\n', 'D\n']
    )


def test_relative_path():
    path = helpers.relative_path(__file__, 'fixtures/glob/0.csv')
    assert open(path).read() == 'empty\n'
