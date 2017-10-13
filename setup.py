import os
from setuptools import setup, find_packages
from thecurator import __version__

# Use a consistent encoding
from codecs import open

here = os.path.abspath(os.path.dirname(__file__))


# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='The Curator',
    version='.'.join(map(str, __version__)),
    packages=find_packages(exclude=['tests']),
    long_description=long_description,
    keywords='import modules packages files',
    license='Proprietary',
    author='Faraz Yashar',
    author_email='faraz.yashar@gmail.com',
    url='https://github.com/fny/thecurator',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3'
    ],
    install_requires=[
        'addict',
        'jinja2',
        'jsonschema',
        'pyaml',
        'sqlalchemy'
    ],
    extras_require={
        'dev': [
            'dateparser',
            'pytest'
        ]
    }

)
