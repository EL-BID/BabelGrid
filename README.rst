=====
S2-py
=====


.. image:: https://img.shields.io/pypi/v/s2.svg
        :target: https://pypi.python.org/pypi/s2

.. image:: https://img.shields.io/travis/JoaoCarabetta/s2.svg
        :target: https://travis-ci.org/JoaoCarabetta/s2

.. image:: https://readthedocs.org/projects/s2-py/badge/?version=latest
        :target: https://s2-py.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


A light wrapper over `s2sphere <https://github.com/sidewalklabs/s2sphere>`_ to mirror
`H3-py <https://github.com/uber/h3-py>`_ API calls.

Installing
-----------
.. code:: python

   pip install s2


Using
-----

Import It

.. code:: python

    from s2 import s2

Get a s2 square given a point

.. code:: python

     lat, lon, res = 12, -3, 10
     s2_address = s2.geo_to_s2(lat, lon, res)

Get the boundaries of a s2 square

.. code:: python

        s2.s2_to_geo_boundary(s2_address)

Get squares of a resolution within a polygon

.. code:: python

        s2.polyfill(geo_json, res)

Features
--------

Table of functions to be implemented in order of priority


+--------------------------+--------------+-------+
| h3 functions             | implemented? | issue |
+--------------------------+--------------+-------+
| geo_to_h3                | yes          |       |
+--------------------------+--------------+-------+
| h3_to_geo                | yes          |       |
+--------------------------+--------------+-------+
| h3_to_geo_boundary       | yes          |       |
+--------------------------+--------------+-------+
| polyfill                 | yes          |       |
+--------------------------+--------------+-------+
| hex_ring                 | no           |       |
+--------------------------+--------------+-------+
| k_ring                   | no           |       |
+--------------------------+--------------+-------+
| k_ring_distances         | no           |       |
+--------------------------+--------------+-------+
| h3_set_to_multi_polygon  | no           |       |
+--------------------------+--------------+-------+
| h3_to_parent             | no           |       |
+--------------------------+--------------+-------+
| h3_to_children           | no           |       |
+--------------------------+--------------+-------+
| hex_range                | no           |       |
+--------------------------+--------------+-------+
| hex_area                 | no           |       |
+--------------------------+--------------+-------+
| edge_length              | no           |       |
+--------------------------+--------------+-------+
| num_hexagons             | no           |       |
+--------------------------+--------------+-------+
| h3_indexes_are_neighbors | no           |       |
+--------------------------+--------------+-------+
| h3_distance              | no           |       |
+--------------------------+--------------+-------+
| h3_line_size             | no           |       |
+--------------------------+--------------+-------+

Credits
-------

* Free software: MIT license

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
    