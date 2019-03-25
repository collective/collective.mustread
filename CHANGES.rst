Changelog
=========


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
