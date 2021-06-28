Changelog
=========


2.0.2 (2021-06-28)
------------------

- Fix a deprecation warning [ale-rt]


2.0.1 (2021-05-20)
------------------

- The ``most_read`` method does not break when trying to fetch objects
  that the user cannot view. Fixes #14 [ale-rt]


2.0.0 (2020-01-27)
------------------

- Indicate end of database initialization in logs [thet]
- Support Plone 5.2 and Python2.7, Python 3.6 and Python 3.7 [ale-rt, thet]


1.1.1 (2019-03-25)
------------------

- Do not break on the upgrade step that adds columns to the mustread table
  [ale-rt]


1.1.0 (2017-05-11)
------------------

- Added the possibility to specify engine parameters through the registry
  [ale-rt]

- remove unneeded columns in ORM model (site_name, title, info) [fRiSi]

- Implemented API for scheduling items as must-read for certain users.
  (see collective.contentrules.mustread for usage)

  This required new database columns. The provided upgrade step works for sqlite databases
  but might need changes for mysql or postgres. [fRiSi]

- Allow to create and configure a database file by using the `@@init-mustread-db` view
  [fRiSI]


1.0.1 (2016-12-28)
------------------

- Provide verbose error logging when database is not accessible [gyst]

- Trivial testing change [gyst]



1.0 (2016-11-24)
----------------

- Initial release.
  [gyst]
