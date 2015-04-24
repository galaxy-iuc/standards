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
    ├── README.rst
    └── tools/
        └── NAME
            ├── macros.xml
            ├── my_tool.xml
            ├── other_tool.xml
            ├── test-data/
            └── tool_dependencies.xml

The highest level directory contains only a few folders for the major types of
Galaxy repositories; tools, packages, data managers, and sometimes visualizations and datatypes.

ToolShed Repositories
---------------------

A Github repository many correspond to any number of published ToolShed
repositories.

Every unrestricted tool shed repository should contain a README_ file -
named either ``README`` or ``README.txt`` (if plain text) or ``README.rst``
(if reStructuredText_). A reStructuredText ``README.rst`` is generally
preferred. For a good example of such a file - please see Peter Cock's NCBI
Blast+ Suite's `README.rst
<https://github.com/peterjc/galaxy_blast/blob/master/tools/ncbi_blast_plus/README.rst>`__.

The Tool Shed recognizes many more types of README files than this - but these
are not encouraged and may be deprecated in the future. Markdown_ is not
supported by the Tool Shed at this time and so ``README.md`` are not
recognized at all.

Package Repositories
--------------------

These may only contain a ``tool_dependencies.xml`` file

Tools
-----

Tool often contain:

* Tool XML files
* ``macros.xml`` file for use in keeping tools DRY
* ``test-data/`` directory, because all tools need test data
* ``tool-data/`` directory, for things like ``*.loc`` files
* ``tool_dependencies.xml`` file for specifying associated packages

.. _README: http://en.wikipedia.org/wiki/README
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Markdown: https://help.github.com/articles/github-flavored-markdown/
