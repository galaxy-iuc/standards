Data Tables
===========

Galaxy data tables let tools present a menu of reference data (for example,
genomes or indexes) to users. Follow the rules below when adding a new data
table. The reference data is stored centrally, which saves space and time
for users.

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

Every new data table must be accompanied by a Data Manager that populates it.
Without a Data Manager, the table would have to be filled in manually by the
administrators of the Galaxy instances that install the tool. That workload
cannot be offloaded to administrators: providing the data also means keeping
it up to date, so the process should be simplified as much as possible
instead of introducing manual work.

Publishing entries to CVMFS
---------------------------

Galaxy Project now offers a way to add new data table entries to the CVMFS.
Entries published there are available to all Galaxy instances using CVMFS,
and are in particular used by all ``usegalaxy.*`` servers.
To request a new entry, see
`Requesting reference data in the Galaxy project IDC documentation
<https://github.com/galaxyproject/idc/blob/main/docs/requesting-reference-data.md>`__.
