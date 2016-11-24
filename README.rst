.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

==============================================================================
collective.mustread
==============================================================================

Track reads on content objects in Plone.

Features
========

- Mark objects as must-read

- Keep a record of first reads of content objects per user

- Query if a specific user has read a specific content object

- List top-x of content objects by user reads in a specific time window


Limitations
-----------

This is not a install-and-forget plugin for Plone.

This product *does not track reads out of the box*.
It merely provides a backend you can use for doing so.

Development of this backend was sponsored by Quaive.
Quaive has it's own frontend integration on top of this backend to cater for the specific use cases Quaive needs. We hope that this generic backend is useful for other Plone projects as well.

Rationale
---------

If you'd want a naive implementation to track reads, you could simply
create a behavior that stores a list of user ids on every content object.

Obviously that would soon destroy your site with database writes.

Instead, this backend is designed to:

- Be compatible with async scheduling, even if it does not provide async itself.

- Be flexible to support multiple policy scenarios, without having to rewrite or fork the whole backend.

- Use a pluggable SQL backend instead of the ZODB, both to offload writes and to make it easier to run reporting queries.

Architecture
============

You're forgiven for thinking the architecture below is overly complex.
Please see the rationale above.

Not included in ``collective.mustread`` is the frontend and async part::

     [ user browser ]  -> [ view ] -> [ async queue  ]

The backend implementation in this package provides the following::

     [ @@mustread-hit ] -> [behavior] -> [database store]

Let's narrate that starting at the database end.

Database
--------

The database storage provides a rich API as specified in ``collective.mustread.interfaces.ITracker``.

Note that the API design already contains specifications for some future extensions that have not been implemented yet.

The SQL store is derived from the ``collective.auditlog`` implementation.
We've designed ``collective.mustread`` to be compatible with ``collective.auditlog`` to the point where we'll even re-use the database connector from auditlog if possible.

The database connection is configured via a registry record ``collective.mustread.interfaces.IMustReadSettings``. You typically want this to contain the same value as your auditlog configuration.

Behaviors
---------

We provide two behaviors:

- ``IMaybeMustRead`` basically only provides a checkbox where you can specify whether a content object is 'must-read'.

- ``ITrackReadEnabled`` activates view tracking on a content object. We track views even if ``IMaybeMustRead`` does not mark the object as 'must-read'. The reason for this is we'd like to track popular content even if the items are not compulsory.

You'd typically activate both these behaviors on the content types you'd like to track.

These behaviors are not activated by default - the ``:default`` install profile only provides a browser layer and configures the database connector. It's up to you to choose and implement your tracking policy in your own projects.

The behaviors provide a flex point where you can implement different tracking policies. You could create a behavior that only tracks reads for certain groups of users for example. You can easily do that by creating a new behavior in a few lines of code, with some extra business logic, which then re-uses our extensive read tracking API for the heavy lifting.

View
----

A helper view ``@mustread-hit`` is available for all ``ITrackReadEnabledMarker`` i.e. all objects with the ``ITrackReadEnabled`` behavior activated. Hitting that view will store a read record in the database for the content object.

In Quaive we will hit this view from our async stack.

You could conceivably, instead of this view, provide a viewlet that accesses the tracking behavior and API. Just be aware that doing all of that full sync is a risk. YMMV.

There's also a special debugging view ``@@mustread-hasread`` which will tell you whether the user you're logged in as, has read the object you're calling this view on.


Installation
============

Install collective.mustread by adding it to your buildout::

    [buildout]

    ...

    eggs =
        collective.mustread


and then running ``bin/buildout``

Or use the built-in buildout::

  virtualenv .
  bin/pip install -r requirements.txt
  bin/buildout bootstrap
  bin/buildout

Using collective.mustread
-------------------------

The minimal steps required to actually use ``collective.mustread`` in your own project:

1. Install ``collective.mustread`` and configure a database connector. The default connector is a in-memory database which is not suitable for production.

2. Activate the ``IMaybeMustRead`` and ``ITrackReadEnabled`` behaviors on the content types you'd like to track, via GenericSetup. Or roll your own custom behaviors.

3. For these content types, hit ``${context/absolute_url}/@@mustread-hit`` when viewing the content. Ideally you'll use some kind of async queue at this stage.

4. Use the tracker API to query the database and adjust your own browser views based on your own business logic. The recommended way to obtain the tracker is::

     from collective.mustread.interfaces import ITracker
     from zope.component import getUtility

     tracker = getUtility(ITracker)


Contribute
==========

- Issue Tracker: https://github.com/collective/collective.mustread/issues
- Source Code: https://github.com/collective/collective.mustread


Support
=======

If you are having issues, please let us know via the issue tracker.

License
=======

The project is licensed under the GPLv2.
