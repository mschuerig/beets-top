
A plugin for Beets to find the top artists, genres, etc. in a music library.

See beets at http://beets.radbox.org/

Please note that this code is not yet settled and will likely change in incompatible ways.


Syntax
------

Examples::

  $ beet top artists
  $ beet top 100 artists
  $ beet top artists by albums
  $ beet top 42 artists by time in year:1990
  $ beet top genres by tracks
  $ beet top years by albums

In general::

  $ beet top [<count>] {artists, albumartists, formats, genres, labels, years, composers} [by {albums, tracks, time}] [in <subquery>]


Installation
------------

TODO not a pythonista here, I need to figure this out myself


Authors
-------

Beets-top is by `Michael Schürig`_.

.. _Michael Schürig: mailto:michael@schuerig.de

