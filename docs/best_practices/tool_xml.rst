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
warning messages appear).

Booleans
--------

truevalue and falsevalue should have the actual parameter included. This
makes it really easy to reference the param-name in the cheetah command
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

The command tag should be started and finished by a CDATA tag, allowing
direct use of characters like the ampersand (``&``) without needing XML
escaping (``&``).

.. code:: xml

    <![CDATA[ your lines of cheetah here ]]>

`Wikipedia has more on CDATA <http://en.wikipedia.org/wiki/CDATA>`__

Help tag
--------

The help tag should be started and finished by a CDATA tag.

.. code:: xml

    <![CDATA[ your lines of restructuredText here ]]>

`http://en.wikipedia.org/wiki/CDATA <http://en.wikipedia.org/wiki/CDATA>`__

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

    ln -sfn $input\_fasta tmp.fa;

before data processing in order to be able to easily generate the
indices without attempting to write to a (possibly) read-only data
source.

Datatypes
---------

TODO

DataManagers
------------

TODO

Coding Style
------------

* 4 spaces indent
* order of XML elemets:

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

* cheetah code should be mainly PEP8 conform
* large XML tags should be broken into several lines

  * label and help can be on a new line 

* variable names should be readable and understandable, preferable the long parameter name
* Order of parameter attributes

  *  name
  *  type
  *  [size]
  *  value | truevalue | falsevalue
  *  [checked]
  *  label
  *  help 

.. _description: https://wiki.galaxyproject.org/Admin/Tools/ToolConfigSyntax#A.3Cdescription.3E_tag_set
.. _macros: https://wiki.galaxyproject.org/Admin/Tools/ToolConfigSyntax#Macro_Token
.. _requirements: https://wiki.galaxyproject.org/Admin/Tools/ToolConfigSyntax#A.3Crequirements.3E_tag_set
.. _stdio: https://wiki.galaxyproject.org/Admin/Tools/ToolConfigSyntax#A.3Cstdio.3E.2C_.3Cregex.3E.2C_and_.3Cexit_code.3E_tag_sets
.. _version_command: https://wiki.galaxyproject.org/Admin/Tools/ToolConfigSyntax#A.3Cversion_command.3E_tag_set
.. _command: https://wiki.galaxyproject.org/Admin/Tools/ToolConfigSyntax#A.3Ccommand.3E_tag_set
.. _configfiles: https://wiki.galaxyproject.org/Admin/Tools/ToolConfigSyntax#A.3Cconfigfiles.3E_tag_set
.. _inputs: https://wiki.galaxyproject.org/Admin/Tools/ToolConfigSyntax#A.3Cinputs.3E_tag_set
.. _outputs: https://wiki.galaxyproject.org/Admin/Tools/ToolConfigSyntax#A.3Coutputs.3E_tag_set
.. _tests: https://wiki.galaxyproject.org/Admin/Tools/ToolConfigSyntax#A.3Ctests.3E_tag_set
.. _help: https://wiki.galaxyproject.org/Admin/Tools/ToolConfigSyntax#A.3Chelp.3E_tag_set
.. _citations: https://wiki.galaxyproject.org/Admin/Tools/ToolConfigSyntax#A.3Ccitations.3E_tag_set
