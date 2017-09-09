ToolShed Readiness Checklist
============================

The process from writing a tool to getting it into a ToolShed can be long and
arduous and confusing. This checklist should assist in making sure you have
done everything required for a great, easy to use Galaxy Tool!

Before ToolShed
---------------

- A `GitHub <https://github.com/>`__ repository should exist for your wrappers, either one you own, or perhaps you are contributing to the `IUC's repository <https://github.com/galaxyproject/tools-iuc>`__.
- A tool directory should exist for the specific set of tools or related functionality you are wrapping.
- Check `Bioconda <https://bioconda.github.io/>`__ for available packages required for the tool you are wrapping. If they do not exist, you may need to create them. The `IUC <https://gitter.im/galaxy-iuc/iuc>`__ will be happy to help you with doing this.
- `Planemo <http://planemo.readthedocs.io/en/latest/readme.html>`__ should be installed (``pip install -U planemo``)
- You will need to have credentials to access your ToolShed (either the `Main
  ToolShed <https://toolshed.g2.bx.psu.edu/>`__, or your local Galactic ToolShed).

Creating the Tool Wrapper
-------------------------

- Review the `IUC Best Practices here <http://galaxy-iuc-standards.readthedocs.io/en/latest/best_practices/tool_xml.html>`__.
- Create your tool wrapper (XML file) with a command like ``planemo tool_init --id 'tool_name' --name 'Tool description'``. 
- Alternatively, you could copy and modify `an existing IUC wrapper <https://github.com/galaxyproject/tools-iuc/tree/master/tools>`__.
- Create an appropriate tool name and ID by consulting the `IUC's Best Practices <http://galaxy-iuc-standards.readthedocs.io/en/latest/best_practices/tool_xml.html>`__.
- Define a version number for the tool. 
- Fill in your requirements section with the conda package(s) name(s) and version number(s).
- Add the command tag. The command to run the tool must be within `CDATA tags <https://en.wikipedia.org/wiki/CDATA>`__, written in `Cheetah <http://cheetahtemplate.org/>`__ and conform to `PEP 8 <http://pep8.org/>`__.
- Supply at least one input with a description of parameters.
- Supply at least one output with a description of parameters.
- Supply at least one tool test. The primary output is a good choice for testing. Don't
  forget the use of ``sim_size`` if variable data is included.
- Add a help section written in `valid reStructuredText <http://docutils.sourceforge.net/rst.html>`__.
- Add a citation section with a citation for the tool, preferably a `DOI <http://www.doi.org/>`__.
- If your tool uses ``tool-data``:
    - Provide the comment-only ``tool-data/data_table_name.loc.sample`` file
    - Provide the comment-only ``tool_data_table_conf.xml.sample`` file

Testing Your Tool
-----------------

- Fill test-data directory with at least one input file and the expected
  output file. 
- It is strongly encouraged that you use small test data sets, ideally
  under 1 Mb. Every Galaxy instance that downloads your tool will
  have to download an entire copy of the test data. If the sum of your
  test-data files is larger than that, consider use of the ``contains``
  test.
- If your tool uses tool-data: 
    - Provide a ``tool_data_table_conf.xml.test`` file, which is an uncommented version of ``tool_data_table_conf.xml.sample`` containing the path to the loc file for testing: ``<file path="${__HERE__}/test-data/data_table_name.loc" />``
      (Please note the use of ``${__HERE__}`` to indicate the directory where the tool is).
    - Provide the .loc file: ``test-data/data_table_name.loc``
    - For a good example of how to test parameters from data tables, please see the `Bowtie example here <https://github.com/galaxyproject/tools-devteam/tree/master/tools/bowtie_wrappers>`__.
- Check your tool XML with ``planemo lint``.
- Run functional tool tests in a local Galaxy with ``planemo test``.
- Serve the tool on a local Galaxy instance for manual verification that everything looks as expected with the ``planemo serve`` command.

Uploading Your Tool to a ToolShed
----------------------------------

- Ensure you have a ``.shed.yml`` file with the appropriate contents.
- Check the ``.shed.yml`` with ``planemo shed_lint``.
- Create the remote repository with ``planemo shed_create --shed_target [toolshed|your_local_shed:9000]``.

Adding Your Tool to the IUC Repository
--------------------------------------

- `Create an issue on IUC GitHub <https://github.com/galaxyproject/tools-iuc/issues>`__ tracking your progress and ensuring that no one else is working on the same tool.
- Fork IUC GitHub on your GitHub account.
- Clone the corresponding repository ``git clone https://github.com/<YOUR_NAME>/tools-iuc tools-iuc``
- Within that folder, create a corresponding branch with ``git checkout -b
  $branch_name``. You might name it after the tool.
- After you have tested your tool and are completely happy with it (per
  previous sections of this document), add your tool and all associated data,
  then Commit the changes with ``git commit -m "I changed X, Y, and Z"``. Finally push your changes to github with ``git push origin $branch_name``.
- Go to the `IUC's Repository <https://github.com/galaxyproject/tools-iuc>`__ and click on 'Compare & Pull Request'.
- Add a comment describing what the tool and any extra information that might
  be needed (E.g. "I had some trouble with the data tables, can someone please
  double check them").
- The IUC will review your tool for inclusion.
- Note that any Python code submitted must conform to `PEP 8 <http://pep8.org/>`__.
