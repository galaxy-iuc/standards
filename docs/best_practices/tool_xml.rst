Tools
=====

Before you start writing a new tool please search the `Main Tool Shed
(MTS) <https://toolshed.g2.bx.psu.edu>`__ and the `Test Tool Shed
(TTS) <https://testtoolshed.g2.bx.psu.edu>`__ because it's possible that
someone has already created a wrapper for the same third party
executable you are looking for. Consider announcing your tool project on
galaxy-dev to see if anyone has already created a wrapper.

Tool versions
-------------

Tool versions are mandatory to enable reproducibility. Version is an
attribute of the XML tool element, e.g.

.. code:: xml

    <tool id="rgTF" name="Tool Factory" version="1.11">

and should be incremented with each change of the wrapper that is
released to the Tool Shed (except for cosmetic modifications).

The value should follow the
`PEP 440 <https://www.python.org/dev/peps/pep-0440/>`__ specification.

If the Galaxy tool is a wrapper for an underlying tool, we recommend to:

- define a ``@TOOL_VERSION@``
  `macro token <https://planemo.readthedocs.io/en/latest/writing_advanced.html#macro-tokens>`__,
  which you should also re-use in the corresponding ``<requirement>`` element;
- optionally, define a ``@VERSION_SUFFIX@`` macro token, which may be placed
  either in the tool wrapper or in a shared macro file. This should be set to
  an integer number:

  - starting at 0 for the first wrapper release of each version of the
    underlying tool;
  - to be increased by 1 whenever you update the wrapper without changing
    the underlying ``@TOOL_VERSION@``.
- set the tool ``version`` attribute to ``@TOOL_VERSION@+galaxy@VERSION_SUFFIX@``. If it
  is preferred not to use a ``@VERSION_SUFFIX@`` token (e.g. to allow bumping
  the version only for a specific tool in a suite), the tool ``version``
  attribute should be simply set to ``@TOOL_VERSION@+galaxyN``, where N is an
  integer following the same rules as ``@VERSION_SUFFIX@``.

If instead the Galaxy tool cannot be identified with a single underlying tool,
the ``+galaxy@VERSION_SUFFIX@`` local version identifier should be omitted, and any version
value can be used, as long as it respects the PEP 440 specification.

For tools whose wrapper version is (for historical reasons) already greater than
the version of the underlying tool, only the minor version number shall be
increased if this is likely to bring the two version in sync in a reasonable
time.

Tool ids
--------

Should be meaningful and unique also in a larger context. If your tool
is called ``grep`` try to prefix that name with something meaningful.
Objective is to make it easier for Galaxy admins to identify a tool
based on the short ID. Otherwise they would need to use the long
``toolshed/xx/`` id.

Some simple rules for generating tool IDs:

-  Tool IDs should contain only ``[a-z0-9_-]``.
-  Multiple words should be separated by underscore or dashes
-  Suite tools should prefix their ids with the suite name. E.g. ``bedtools_*``


Tool Names
----------

Names are important! Names are how users and admins find your tools. Names
should strive to be unique within a suite of tools, and may wish to include the
suite name if it is a well known suite. Some instructional examples:

-  Cufflinks, Cuffdiff, Cuffmerge are in a suite together.
-  The vsearch suite contains tools with names like "VSearch Alignment",
   "VSearch Clustering", etc.

In the cufflinks example, everyone knows the functionality of the cufflinks
command, and can easily guess as the use of a tool named "cuffdiff" in their
tool panel.

With VSearch however, a tool named "Alignment" would not be useful, as users
would have a hard time finding it and gathering context about its functionality.
With the VSearch prefix, once a user learns what one VSearch tool does, they can
quickly apply that to the other available VSearch tools.

Tool profile
------------

Tools should define a recent profile, i.e. a profile not older than 1 year. 

Tool Descriptions
-----------------

Tool names are not your only tool for making your tool discoverable to end
users, and conveying information regarding the functionality of said tool. Tool
descriptions are displayed directly after the tool name and generally conform to
a "sentence" like structure.

-  ``bowtie2`` is a short read aligner
-  ``Cuffmerge`` merges together several Cufflinks assemblies
-  ``NCBI BLAST+ database info`` shows BLAST database information from blastdbcmd

In the above examples the tool name is rendered in fixed width text, and the
rest is the tool description.

Tool cross-references (bio.tools)
---------------------

It is important to cross-link Galaxy tools to best practice metadata in registries and
catalogs such as `bio.tools <https://bio.tools/>`__.

bio.tools is a global portal for bioinformatics resources that helps researchers to find,
understand, compare and select resources suitable for their work.

You can link a Galaxy tool to its bio.tools entry by adding a ``xref`` snippet
to the tool wrapper: i.e. modifying the ``*.xml`` file. Below is an example ``xml`` for
`Racon <https://github.com/bgruening/galaxytools/tree/1570f3a28232b4b88385cdfbb68f79d80ff1dabb/tools/racon>`__

.. code:: xml
    <macros>
        <import>macros.xml</import>
    </macros>
    <xrefs>
        <xref type="bio.tools">Racon</xref>
    </xrefs>
    <expand macro="requirements" />
    <version_command>racon --version</version_command>
    <command detect_errors="exit_code"><![CDATA[

Please reference only the tool which is wrapped, not the dependencies.

If a bio.tools entry does not exist, you should add an entry as follows:

-   Create an account on bio.tools.
-   Add a new tool, completing as much metadata as possible / available.
-   Ensure that you add at least one EDAM ``Topic`` and one EDAM ``Operation``
    to the entry (see below).

Tool annotations (EDAM)
---------------------

The bio.tools registry makes use of the `EDAM`_ ontology
to annotate tools with ``Data``, ``Format``, ``Operation`` and ``Topic`` terms.

`EDAM`_ terms are used to give a description of the tool's scientific domain and the
functionalities it provides. The `EDAM browser <https://edamontology.github.io/edam-browser/>`__
makes the process of picking EDAM terms much easier.

Once a bio.tools identifier is added as an ``xref`` in the tool wrapper, the easiest way
to improve the available EDAM annotations is to update the bio.tools entry metadata.

Alternatively, you can add EDAM annotations directly to a Galaxy tool by adding the
`edam_topics <https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-edam-topics>`__
and `edam_operations <https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-edam-operations>`__
elements to the tool XML file. This approach is not recommended though, as it risks duplicating the
tool annotation work in multiple places.

When picking EDAM terms, avoid `root terms` such as `Topic` and `Operation`, and pick the
most specific terms available. If you feel like the terms required to describe the tool are
missing, do not hesitate to `ask for new terms <https://edamontologydocs.readthedocs.io/en/latest/getting_involved.html#suggestions-requests>`__.

More detailed guidelines to pick EDAM terms are also available in the [bio.tools curators guide](https://biotools.readthedocs.io/en/latest/curators_guide.html#edamannotations) and the [EDAM ontology users guide](https://edamontologydocs.readthedocs.io/en/latest/users_guide.html#picking-concepts).

Parameter name, argument and help
---------------------------------

The ``argument`` attribute of ``<param>`` should include the long form of the
underlying tool parameter, e.g. ``argument="--max"``. This is automatically
displayed inside the parameter help and is useful to give
the user the chance to go to the original documentation and map the
Galaxy UI element to the actual parameter. It also makes debugging
easier if the user is talking to non-Galaxy developers.

When ``argument`` is specified, the ``name`` attribute becomes optional and, if
not included, is derived from ``argument`` by stripping any leading dashes
and replacing internal dashes by underscores (the later since release 19.09). This
derived name can be used inside the ``<command>`` element to refer to the
parameter value as you would normally do with the ``name`` attribute.
Note that if the automatically generated name violates the rules for valid Cheetah 
placeholders (i.e. consist of alphanumeric characters or underscore and must not
start with a digit) you should specify a valid ``name`` attribute for the parameter.

Tests
-----

All Galaxy Tools should include functional tests. In their simplest
form, you provide sample input files and expected output files for given
parameter values. Where the output file is not entirely reproducible you
can make assertions about the output file contents.

Testing error conditions is also important. Recent development now
allows tests say if the test should fail, and to make assertions about
the tool's stdout and stderr text (e.g. check expected summary text or
warning messages appear). See `planemo docs <https://planemo.readthedocs.io/en/latest/writing_how_do_i.html#test-failure-states>`__ for more information.

When tools contain output filters, tests should be included that verify
this filtering occurs. See `planemo docs <https://planemo.readthedocs.io/en/latest/writing_how_do_i.html#test-output-filters-work>`__ for more information.

Data parameters
---------------

If a compressed version of a datatype (e.g. ``fasta.gz`` or ``fastqsanger.bz2``)
is supported by Galaxy, then data parameters should accept both the compressed
and the uncompressed datatypes. The tool should internally decompress the
dataset if the underlying tool cannot handle the compressed formats natively.

Booleans
--------

``truevalue`` and ``falsevalue`` attributes of ``<param>`` should contain the
underlying tool parameter. This makes it really easy to reference the param name
in the Cheetah ``<command>`` section.

.. code:: xml

    <command>
    ...
    $strict
    ...
    </command>
    <inputs>
        ...
        <param name=”strict” truevalue=”--enable-strict” falsevalue=””>

Boolean should not be used as a conditional for other options. For dynamic
options, please use a ``select`` input type as described in the Dynamic Options
section below.

Dynamic Options
---------------

Options that are conditionally hidden (using the ``<conditional>`` element)
should use a ``select`` param type and not a ``boolean``. The user may not
expect a boolean checkbox to change the content of a form.

To create an "Advanced options" section which is normally hidden and the user
can expand, a ``<section>`` element can be used instead of a ``<conditional>``.
Beware that parameters inside a hidden section still have a value set, which is
used when creating the job command, while in a "closed" conditional the
non-visible parameters don't have a value.

Command tag
-----------

The command tag is one of the most important parts of the tool, next to the
user-facing options. It should be highly legible.

Command Formatting
^^^^^^^^^^^^^^^^^^

The command tag should be started and finished by a CDATA tag, allowing
direct use of characters like the ampersand (``&``) without needing XML
escaping (``&amp;``).

.. code:: xml

    <![CDATA[ your lines of Cheetah here ]]>

`Wikipedia has more on CDATA <http://en.wikipedia.org/wiki/CDATA>`__

All Cheetah variables for text parameters, input and output files must be
single-quoted, e.g. ``'${var_name}'``.

For composite datatypes the recommended attribute to access the associated
directory name differs for inputs (e.g. ``$input.extra_files_path``) versus
outputs (e.g. ``$output.files_path``). This difference is historical, and
it is hoped this will be harmonised in a future Galaxy release.

If you need to execute more than one shell command, concatenate them with a
double ampersand (``&&``), so that an error in a command will abort the
execution of the following ones.

Exit Code Detection
^^^^^^^^^^^^^^^^^^^

Unless the tool has special requirements, you should take advantage of the exit
code detection provided by Galaxy, in lieu of using the ``<stdio/>`` tags. This
can be done by adding a ``detect_errors`` tag to your ``<command />`` block like
so:

.. code:: xml

    <command detect_errors="aggressive">
    ...
    </command>

This will automatically fail the tool if the exit code is non-zero, or if the
phrases ``error:`` or ``exception:`` appear in STDERR.


Help tag
--------

The help tag should be started and finished by a CDATA tag.

.. code:: xml

    <![CDATA[ your lines of restructuredText here ]]>

`http://en.wikipedia.org/wiki/CDATA <http://en.wikipedia.org/wiki/CDATA>`__

Inside the help tag you should describe the functionality of your tool.
The help tag is to the ``help=""`` attribute as a man page is to the ``--help``
flag. The help tag should cover the tools functionality, use cases, and even
known issues in detail. The help tag is a good place to provide examples of how
to run the tool and discuss specific subcases that your users might be
interested in.

Including Images
^^^^^^^^^^^^^^^^

If you have produced images detailing how your tool works (e.g. `bedtools`_), it
might be nice for those images to be included in the Galaxy tool documentation!

Images should be placed in a subdirectory, ``./static/images/``, and referenced
in your tool help as ``.. image:: my-picture.png``. This can be seen in the
IUC's wrappers, such as the one for the bedtools `slop`_ command.

Generating Indices
------------------

Occasionally data needs to be indexed (e.g. bam, fasta) files. When data
is indexed, those indices should be generated in the current working
directory rather than alongside the input dataset. This is part of the
tool contract, you can read from your inputs, but only write to your
outputs and CWD.

It's convenient to do something like:

.. code:: console

    ln -sfn "${input_fasta}" tmp.fa;

before data processing in order to be able to easily generate the
indices without attempting to write to a (possibly) read-only data
source.

Datatypes
---------

For now, the recommended practice is to push new datatypes to the
`Galaxy repository`_.

Data Managers
-------------

TODO

Coding Style
------------

* 4 spaces indent
* Order of XML elements:

  * `description`_
  * `macros`_
  * `edam_topics`_
  * `edam_operations`_
  * `xrefs`_
  * [parallelism]
  * `requirements`_
  * [code]
  * `stdio`_
  * `version_command`_
  * `command`_
  * environment_variables
  * `configfiles`_
  * `inputs`_
  * `request_param_translation`_
  * `outputs`_
  * `tests`_
  * `help`_
  * `citations`_

* Cheetah code should also be indented and mainly `PEP8`_ conformant
* XML elements should normally have all attributes on a single line for easier
  searchability, but for large XML elements the ``label`` and ``help``
  attributes can be on a new line.

* param names should be readable and understandable, e.g. using the long option name of the wrapped tool
* Order of parameter attributes:

  * name
  * argument
  * type
  * format
  * min | truevalue
  * max | falsevalue
  * value | checked
  * optional
  * label
  * help

* Python code should be Python3-compatible and `PEP8`_ conformant. Imports should
  follow the `smarkets`_ style.

.. _description: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-description
.. _xrefs: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-xrefs
.. _macros: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-macros
.. _edam_topics: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-edam-topics
.. _edam_operations: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-edam-operations
.. _requirements: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-requirements
.. _stdio: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-stdio
.. _version_command: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-version-command
.. _command: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-command
.. _configfiles: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-configfiles
.. _inputs: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-inputs
.. _request_param_translation: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-request-param-translation
.. _outputs: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-outputs
.. _tests: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-tests
.. _help: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-help
.. _citations: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-citations
.. _bedtools: http://bedtools.readthedocs.org/en/latest/content/tools/slop.html
.. _slop: https://github.com/galaxyproject/tools-iuc/blob/master/tools/bedtools/slopBed.xml
.. _Galaxy repository: https://github.com/galaxyproject/galaxy
.. _PEP8: https://www.python.org/dev/peps/pep-0008/
.. _smarkets: https://github.com/PyCQA/flake8-import-order/blob/master/tests/test_cases/complete_smarkets.py
.. _bio.tools: https://bio.tools
.. _EDAM: http://edamontology.org
