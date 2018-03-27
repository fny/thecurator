import os
from setuptools import setup, find_packages
from thecurator import __VERSION__

# Use a consistent encoding
from codecs import open

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='thecurator',
    version='.'.join(map(str, __VERSION__)),
    packages=find_packages(exclude=['tests']),
    package_data={'thecurator': ['table_description_schema.yml']},
    long_description=long_description,
    keywords='',
    license='Proprietary',
    author='Faraz Yashar',
    author_email='faraz.yashar@gmail.com',
    url='https://github.com/fny/thecurator',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3'
    ],
    install_requires=[
        'jsonschema',
        'pyaml',
        'sqlalchemy'
    ],
    extras_require={
        'dev': [
            'dateparser',
            'pandas',
            'pytest'
        ]
    }

)
