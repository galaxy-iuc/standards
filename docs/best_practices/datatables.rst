Data Tables
===========

Galaxy data tables let tools present a menu of reference data (for example,
genomes or indexes) to users. 

What is a Data Table?
---------------------

A data table is a small, centrally managed table of metadata describing
reference datasets stored on a Galaxy server, such as genome indexes or
BLAST databases. Each row describes one entry with columns such as
``name``, ``value``, and ``path``, and tools expose those entries to users
as a selection menu. A data table is identified by a name and all tool
(versions) using this data table share the same information (but it can
be filtered tool / version specific). Because the underlying files are shared across all
users of a server, a data table saves disk space and lets users pick
ready-made data instead of uploading it themselves.

Design the columns for a Data Manager
-------------------------------------

Once a data table is deployed on the Tool Shed, its columns must never be
changed. Hence it is worth devoting some time to the column design. Include
at least the ``name``, ``value``, and ``path`` columns (and ``dbkey`` for
genomic data). The version of the data and/or of the software generating the
data has also proven useful, as have any other fields that help tools and
users select a meaningful value automatically.

A Data Manager is required
--------------------------

It is strongly recommended to accompany every new data table by a Data Manager that populates it.
Without a Data Manager, the table would have to be filled in manually by the
administrators of the Galaxy instances that install the tool. That workload
cannot be offloaded to administrators: providing the data also means keeping
it up to date, so the process should be simplified as much as possible
instead of introducing manual work.
`A tutorial on data manager is available at GTN
<https://training.galaxyproject.org/training-material/topics/dev/tutorials/data-manager-architecture/tutorial.html>`__.

Publishing entries to CVMFS
---------------------------

Galaxy Project now offers a way to add new data table entries to the CVMFS.
Entries published there are available to all Galaxy instances using CVMFS,
and are in particular used by all ``usegalaxy.*`` servers.
To request a new entry, see
`Requesting reference data in the Galaxy project IDC documentation
<https://github.com/galaxyproject/idc/blob/main/docs/requesting-reference-data.md>`__.
