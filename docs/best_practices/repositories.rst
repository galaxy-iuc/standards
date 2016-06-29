Github Repositories
===================

Most tool developers are on GitHub, and have chosen to lay out their
repositories in a structure similar to the following:

.. code::

    tools-iuc/
    ├── data_managers
    │   └── data_manager_NAME/...
    ├── LICENSE
    ├── packages/
    │   └── package_NAME_VERSION/tool_dependencies.xml
    ├── README.rst
    ├── suites/
    │   └── suite_name/...
    └── tools/
        └── NAME
            ├── macros.xml
            ├── my_tool.xml
            ├── CHANGELOG.md
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


Suites
------

The Toolshed offers the concept of a suite which is simply a meta-package
listing several other packages. For example the ``suite_hmmer_3`` provides a
package that depends on all of the individual ``hmmer_.*`` packages, defined by
a ``repository_dependencies.xml`` file:

.. code-block:: xml

    <repositories description="HMMER v3 HMM based sequence alignment and database search tools">
      <repository changeset_revision="ddda6eae7b23" name="hmmer_hmmemit" owner="iuc" toolshed="https://testtoolshed.g2.bx.psu.edu" />
      <repository changeset_revision="5ec773098cb9" name="hmmer_hmmconvert" owner="iuc" toolshed="https://testtoolshed.g2.bx.psu.edu" />
      ...

Manually curated suites are most commonly used to package together related
pieces of software by different groups, when that functionality all serves a
common purpose.

Suites should NOT be used for a single set of highly related tools from the
same group, like the hmmer example above, or bedtools. Instead, a suite can be
automatically created for those sets of tools by Planemo_.

Tools
-----

Tool often contain:

* Tool XML files
* ``macros.xml`` file for use in keeping tools DRY
* ``test-data/`` directory, because all tools need test data
* ``tool-data/`` directory, for things like ``*.loc`` files
* ``tool_dependencies.xml`` file for specifying associated packages
* ``CHANGELOG.md`` file for tracking the history of features over time in your tool

.. _README: http://en.wikipedia.org/wiki/README
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Markdown: https://help.github.com/articles/github-flavored-markdown/
.. _Planemo: http://galaxy-iuc-standards.readthedocs.org/en/latest/best_practices/shed_yml.html#advanced-parameters
