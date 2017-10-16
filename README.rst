The Curator 🖼
==============

.. image:: https://travis-ci.org/fny/thecurator.svg?branch=master
   :target: https://travis-ci.org/fny/thecurator
   :alt: Build Status

.. image:: https://badge.fury.io/py/thecurator.svg
   :target: https://pypi.python.org/pypi/thecurator
   :alt: The Curator on PyPI


The Curator helps you define pipelines for transforming dirty data into consumable APIs.


Usage
-----

Curation
~~~~~~~~

.. code:: python
  from thecurator import Curator

  # Paths to files describing different tables
  table_descriptions = ['patient.yml', 'lab.yml']
  curator = Curator(sqlalchemy_engine, table_descriptions)

  # Transform a pandas DataFrame according to the descriptions
  curator.transform_df('patient', patient_df)

  # Transform a dictionary array according to the descriptions
  curator.transform_dicts('patient', patient_dicts)

  # Transform and insert a according to the descriptions
  curator.insert_dicts('lab', lab_dicts)

Table Descriptions
~~~~~~~~~~~~~~~~~~

Every

Transformations
~~~~~~~~~~~~~~~

API Generation
~~~~~~~~~~~~~~

.. code:: python
  from thecurator import Curator




See the tests. More coming soon...


Development
-----------

 - Install development requirements `pip install dev-requirements`
 - Make changes
 - Run the tests `pytest tests`
