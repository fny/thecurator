"""Helper functions used throughout the library"""
import itertools
import glob
import os


def relative_path(__file__, path):
    """Returns the full path for a relative path"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))


def expand_path(__file__, path_with_globs):
    """Returns an array of full paths for a relative path with globs"""
    return glob.glob(relative_path(__file__, path_with_globs))


def expand_paths(__file__, paths_with_globs):
    """Returns full paths for a series relative paths with globs"""
    if isinstance(paths_with_globs, str):
        return expand_path(__file__, paths_with_globs)
    else:
        expanded_globs = [
            expand_path(__file__, path) for path in paths_with_globs
        ]
        # Flatten
        return list(itertools.chain.from_iterable(expanded_globs))
