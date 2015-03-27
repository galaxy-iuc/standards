Github Repositories
===================

Most tool developers are on GitHub, and have chosen to lay out their
repositories in a structure similar to the following:

.. code::

    tools-iuc/
    ├── data_managers
    │   └── data_manager_NAME/
    ├── LICENSE
    ├── packages/
    │   └── package_NAME_VERSION/tool_dependencies.xml
    ├── README.md
    └── tools/
        └── NAME
            ├── macros.xml
            ├── my_tool.xml
            ├── other_tool.xml
            ├── test-data/
            └── tool_dependencies.xml

The highest level directory contains only a few folders for the major types of
Galaxy repositories; tools, packages, data managers, and sometimes visualizations and datatypes.

Packages
--------

These may only contain a ``tool_dependencies.xml`` file

Tools
-----

Tool often contain:

* Tool XML files
* ``macros.xml`` file for use in keeping tools DRY
* ``test-data/`` directory, because all tools need test data
* ``tool_dependencies.xml`` file for specifying associated packages

