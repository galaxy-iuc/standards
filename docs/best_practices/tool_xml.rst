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

Parameter help
--------------

The help section should include the long argument name (but this should
not be in the tool label). E.g. ``help="(--max)"``. This is useful to give
the user the chance to go to the original documentation and map the
Galaxy UI element to the actual parameter. It also makes debugging
easier if the user is talking to non-Galaxy developers.

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

Booleans
--------

truevalue and falsevalue should have the actual parameter included. This
makes it really easy to reference the param name in the Cheetah command
section.

.. code:: xml

    <param name=”strict” truevalue=”--enable-strict” falsevalue=””>
    $strict

Boolean should not be used as conditionals. For conditionals please use
a select type as described in Dynamic Options below.

Dynamic Options
---------------

Certain options such as "Advanced Options" should be a select box and
not a boolean. A checkbox is not expected to change the content of the
mask from a user point of view.

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


Tool Dependency Package
-----------------------

If you are using perl/ruby/python/R packages, use the corresponding
``*_environment`` tags to depend on a specific version of Perl/Ruby ...

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

For now, the recommended practice is to push new datatypes to the `Galaxy`_
repository.

Data Managers
-------------

TODO

Coding Style
------------

* 4 spaces indent
* Order of XML elements:

  * `description`_
  * `macros`_
  * `requirements`_
  * [code]
  * `stdio`_
  * `version_command`_
  * `command`_
  * environment_variables
  * `configfiles`_
  * `inputs`_
  * `outputs`_
  * `tests`_
  * `help`_
  * `citations`_

* Cheetah code should also be indented and mainly PEP8 conformant
* Large XML elements may be broken into several lines

  * label and help attributes can be on a new line

* param names should be readable and understandable, e.g. using the long option name of the wrapped tool
* Order of parameter attributes:

  *  name
  *  type
  *  value | truevalue | falsevalue
  *  [checked]
  *  label
  *  help 

.. _description: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-description
.. _macros: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-macros
.. _requirements: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-requirements
.. _stdio: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-stdio
.. _version_command: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-version-command
.. _command: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-command
.. _configfiles: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-configfiles
.. _inputs: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-inputs
.. _outputs: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-outputs
.. _tests: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-tests
.. _help: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-help
.. _citations: https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-citations
.. _bedtools: http://bedtools.readthedocs.org/en/latest/content/tools/slop.html
.. _slop: https://github.com/galaxyproject/tools-iuc/blob/master/tools/bedtools/slopBed.xml
.. _Galaxy: https://github.com/galaxyproject/galaxy
