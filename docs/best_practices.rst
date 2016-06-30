Best Practices for Creating Galaxy Tools
========================================

This page is written by experienced tool developers and contains
information about what practices in Galaxy tool development tend to be
the most successful ones.

Why you might read this
-----------------------

If you need to maintain existing tools or develop new tools for Galaxy,
this programmer oriented guide, contributed by the community, will
detail current collected best practice guidelines for building and
maintaining automatically installing reproducible Galaxy tools.

Definitions
-----------

Follows a short summary of the key parts when it comes to Galaxy Tools.

-  `ToolShed <https://wiki.galaxyproject.org/ToolShed>`__, The Galaxy
   AppStore - companion Galaxy web server for tools. E.g.
   https://toolshed.g2.bx.psu.edu or localhost:9009 for Mercurial based
   source code management and automated installation of all components
   described below through any Galaxy admin interface.
-  Galaxy Tool - An application specific, XML defined interface and
   associated documentation exposing any command line application as a
   form-driven Galaxy tool - e.g. BWA or bamtools. Ideally, as a
   shareable tool shed repository, supporting automated Galaxy
   installation with revision/version specific control of dependency
   binaries for reproducible analyses.
-  Tool Dependency Package - Tool Shed tools in the Tool Dependency
   Packages category whose names start with ``package_`` such as
   ``package_samtools_1_0_0``, automate the installation of a specific
   version of some command line application software that other tools
   depend on. Each dependency package may be shared by many tools and
   are only available to users through tool forms that populate command
   lines and execute them.
-  Datatypes - Galaxy has a flexible and extensible internal
   representation for specialised data formats such as fasta sequences,
   fastq short read data or tabular text persisted in Galaxy histories.
   Tools and packages can extend Galaxy by installing new datatypes when
   needed.
-  DataManagers - Large scale scientific analyses often involve local
   copies of canonical reference data such as reference genomes and
   application specific index files for annotation and mapping in
   genomics. In most cases these are rapidly evolving and a constant
   drain on highly skilled resources to keep up to date manually. Data
   Managers can be built and shared to automate reference data
   maintenance by the local Galaxy administrators. Data Manager
   repositories should start with ``data_manager_``.

Tools and Tool Development
--------------------------

.. toctree::

    best_practices/tool_xml
    best_practices/integration_checklist

Packages
--------

.. toctree::

    best_practices/package_xml


Repository Layout
-----------------

.. toctree::

    best_practices/repositories

.shed.yml
---------

.. toctree::

    best_practices/shed_yml

Repository Management
---------------------

.. toctree::

    best_practices/management

