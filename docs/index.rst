Galaxy Tool Development Standards and Best Practices
======================================================================

Following the extensive efforts put in by developers from the
`Intergalactic Utilities Commission (IUC) <https://galaxyproject.org/iuc>`__ into
developing `Galaxy <https://galaxyproject.org/>`__ tools over the years, we have
collected the best practices below. We recommend them to the Galaxy tool developer
community, both for contributing back to the
`IUC repository <https://github.com/galaxyproject/tools-iuc/>`__ and for use in
their own tool repositories.

Why you might read this
-----------------------

If you need to maintain existing tools or develop new tools for Galaxy, this
community-authored guide describes current best practices for building and
maintaining automatically installable, reproducible Galaxy tools.

Definitions
-----------

The key components involved in Galaxy tool development are:

- `Tool Shed <https://galaxyproject.org/toolshed/>`__: the Galaxy application
  repository. Tool Shed repositories support automated installation of tools
  and their associated components through the Galaxy administration interface.
- Galaxy tool: an XML-defined interface and associated documentation that
  exposes a command-line application as a form-driven Galaxy tool. Tools should
  ideally be shared in a Tool Shed repository with revision-specific dependency
  requirements for reproducible analyses.
- Data Manager: a tool that automates local maintenance of canonical reference
  data, such as reference genomes and application-specific indexes. Data Manager
  repository names should start with ``data_manager_``.

Checklists
----------

Step-by-step lists to work through when preparing a tool.

.. grid:: 1 2 3 3

    .. grid-item-card:: Integration Checklist
        :link: best_practices/integration_checklist
        :link-type: doc

        A step-by-step checklist for getting a tool ready for the Tool Shed.

    .. grid-item-card:: Tool Security Checklist
        :link: best_practices/security
        :link-type: doc

        A security checklist for wrappers, inputs, commands, files, credentials, and downloads.

    .. grid-item-card:: Remote Execution Checklist
        :link: best_practices/pulsar
        :link-type: doc

        A checklist for making tools work when jobs run remotely without a shared filesystem.

Documentation
-------------

Reference guides for the pieces that make up a tool and its repository.

.. grid:: 1 2 3 3

    .. grid-item-card:: Tool XML
        :link: best_practices/tool_xml
        :link-type: doc

        Structure, macros, command sections, tests, and help for tool wrappers.

    .. grid-item-card:: Tool Dependencies
        :link: best_practices/package_xml
        :link-type: doc

        Declaring dependencies with Conda, Bioconda, and containers.

    .. grid-item-card:: Data Managers
        :link: best_practices/data_managers
        :link-type: doc

        Stable data-table identifiers, reproducible downloads, paths, testing,
        and migrations.

    .. grid-item-card:: Licensing and Use Restrictions
        :link: best_practices/licensing
        :link-type: doc

        Licensing requirements, redistribution, declarations, and restricted
        dependencies.

    .. grid-item-card:: Repository Layout
        :link: best_practices/repositories
        :link-type: doc

        How to organize files within a Tool Shed repository.

    .. grid-item-card:: .shed.yml
        :link: best_practices/shed_yml
        :link-type: doc

        Metadata and configuration for Tool Shed repositories.

    .. grid-item-card:: Repository Management
        :link: best_practices/management
        :link-type: doc

        Ongoing maintenance and release practices.

.. toctree::
   :maxdepth: 3
   :caption: Best Practices
   :hidden:

   best_practices/integration_checklist
   best_practices/security
   best_practices/pulsar
   best_practices/tool_xml
   best_practices/package_xml
   best_practices/data_managers
   best_practices/licensing
   best_practices/repositories
   best_practices/shed_yml
   best_practices/management

Galaxy Ecosystem
----------------

- `Galaxy Project <https://galaxyproject.org>`__ -- open-source platform for data-intensive research
- `IUC <https://galaxyproject.org/iuc>`__ -- Intergalactic Utilities Commission, curated community tools
- `Planemo <https://planemo.readthedocs.io>`__ -- CLI for Galaxy tool and workflow development
- `Galaxy Tools for Visual Studio Code <https://marketplace.visualstudio.com/items?itemName=davelopez.galaxy-tools>`__
  -- Galaxy Language Server-powered completion, validation, linting, and more for tool wrappers
- `Galaxy Training Network <https://training.galaxyproject.org>`__ -- tutorials and training materials

Indices and tables
===================

* :ref:`search`
