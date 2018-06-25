The Curator 🖼
==============

.. image:: https://travis-ci.org/fny/thecurator.svg?branch=master
   :target: https://travis-ci.org/fny/thecurator
   :alt: Build Status

.. image:: https://badge.fury.io/py/thecurator.svg
   :target: https://pypi.org/project/thecurator
   :alt: The Curator on PyPI


The Curator helps you define pipelines for transforming dirty data into consumable databases.

Usage
-----

.. code:: python

  from thecurator import Curator

  # Paths to files describing different tables
  table_descriptions = ['patient.yml', 'lab.yml']
  curator = Curator(sqlalchemy_engine, table_descriptions)

  # Transform a pandas DataFrame according to the descriptions
  curator.transform_df('patient', patient_df)

  # Transform a dictionary array according to the descriptions
  curator.transform_dicts('patient', patient_dicts)

  # Transform and insert a dictionary array according to the descriptions
  curator.insert_dicts('lab', lab_dicts)


See the tests for more examples. More coming soon...

Development
-----------

 - Install development requirements `pip install -r dev-requirements.txt`
 - Make changes
 - Run the tests `pytest tests`
 - See the Makefile for other useful commands
