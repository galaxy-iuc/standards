Data Managers
=============

Data Managers install reference data and populate Galaxy tool data tables.
The identifiers emitted by a Data Manager form part of the interface between tools,
workflows, and Galaxy instances.

Stable data-table identifiers
-----------------------------

Installing the same source data on different Galaxy instances or on different
days must produce the same machine-readable identity.

A Data Manager table row commonly contains the following fields:

``value``
    The stable identifier selected by tools and serialized into workflows. It
    must identify the data, not the local installation event.

``dbkey``
    The genome or build identifier, when applicable. It must describe the
    biological build and must not contain an installation timestamp.

``name``
    A human-readable display label. Download dates and other installation
    provenance may be included here.

``path``
    The installed data location. It should be stable or derived from the same
    immutable data identity as ``value``.

Do not use ``date.today()``, ``datetime.now()``, ``utcnow()``, or equivalent
wall-clock values to construct ``value``, ``dbkey``, or an identity-bearing
``path``.

For example, this row is not portable:

.. code-block:: json

    {
      "value": "sylph_downloaded_28082026_OceanDNA-c200-v0.3.syldb",
      "name": "OceanDNA c200 v0.3",
      "path": "sylph/downloaded_28082026/OceanDNA-c200-v0.3.syldb"
    }

A portable row separates data identity from installation provenance:

.. code-block:: json

    {
      "value": "sylph_OceanDNA-c200-v0.3.syldb",
      "name": "Sylph OceanDNA c200 v0.3 (downloaded 2026-08-28)",
      "path": "sylph/OceanDNA-c200-v0.3.syldb"
    }

The two rows may have different ``name`` values on different installations, but
the latter retains the same workflow-facing identity.

Choosing an identity
--------------------

Prefer the most specific immutable identity published by the upstream source:

#. an upstream database release or version;
#. an upstream tag or commit;
#. a versioned manifest;
#. a canonical content digest, such as SHA-256, if no immutable upstream
   identifier exists.

When using a digest for a directory or multi-file database, calculate it from a
deterministic manifest of relative paths and file digests. Do not include
filesystem timestamps, extraction order, or other installation-specific
metadata.

A source snapshot date may be part of the identifier when it is an actual
version assigned by the upstream project. A local download date is provenance
about the installation and is not a source version.

Mutable downloads
-----------------

A URL or API endpoint named ``latest`` does not by itself provide a stable data
identity. Before adding the table row, resolve the download to an immutable
release, commit, manifest version, or content digest.

A Data Manager must not silently reuse an existing identifier when the upstream
content has changed. If the content changes, it must receive a new immutable
identifier.

Display names and provenance
----------------------------

The ``name`` field should be descriptive enough for both administrators and users to
understand which data is installed. It may include:

- the upstream project and database name;
- the release, tag, or snapshot version;
- relevant build parameters;
- the local download date (but only if the other metadata are not enough).

Installation metadata must not be copied into ``value`` or ``dbkey`` merely to
make the display name unique.

Paths
-----

Paths should be derived from a stable data identity rather than the installation
date. This makes configuration reproducible and avoids accumulating a new path
for every execution of the same Data Manager.

Do not overwrite different content under an existing identity. If the resolved
upstream version or content digest has changed, generate a new identifier and
path.

Idempotency
-----------

Running a Data Manager repeatedly for the same immutable data should not create
multiple selector rows with the same ``value``.

If that identity is already installed, the Data Manager should either leave the
existing row unchanged or use keyed replacement semantics. In particular, a new
download date in ``name`` must not cause a duplicate row to be appended.

Testing
-------

Data Manager tests should use stable expected values for ``value``, ``dbkey``,
and identity-bearing paths. Avoid expected values derived from the date on which
the test runs. Installation dates may still appear in assertions about the
human-readable ``name`` when relevant.

Updating existing Data Managers
-------------------------------

Changing an existing table value can break workflows that serialized the old
value. Migrations should therefore preserve compatibility:

#. Retain the existing dated row or provide a legacy alias.
#. Add a stable value pointing to the same installed data.
#. Update workflows and tests to use the stable value.
#. Make subsequent Data Manager versions emit only stable values.
#. Deprecate legacy aliases after an appropriate compatibility period.
