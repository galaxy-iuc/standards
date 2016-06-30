ToolShed Readiness Checklist
============================

The process from writing a tool to getting it on the ToolShed can be long and
arduous and confusing. This checklist should assisst in making sure you have
done everything required for a great, easy to use Galaxy Tool!

Before ToolShed
---------------

- A GitHub repository should exist for your wrappers; either one you own, or
  perhaps you are contributing to the IUC's repository.
- A tool directory should exist for the specific set of tools or related
  functionailty you are wrapping.
- Check on BioConda for available packages which are required for the tool you
  are wrapping. If they do not exist, you may need to create them. The IUC will
  be happy to help you with doing this.
- Planemo should be installed (``pip install -U planemo``)
- You will need to have credentials to access your ToolShed (either the `Main
  ToolShed <https://toolshed.g2.bx.psu.edu/>`__, or your local Galactic ToolShed)

Creating the Tool Wrapper
-------------------------

- Create your tool wrapper with a command like ``planemo tool_init --id 'tool_name' --name 'Tool description'``

    - Find an appropriate name and ID by consulting the IUC's Best Practices List.

- Fill in your requierments section in the Tool file with the conda package's name and version number.
- Add test-data

    - Fill test-data directory with at least one input file and the expected
      output file. The primary output is a good choice for testing. Don't
      forget the use of ``sim_size`` if variable data is included.

- Supply at least one tool test.
- If your tool uses ``tool-data``:

    - Add files to the tool-data folder
    - Provide the related ``data_name.loc.sample`` file
    - Provide the ``tool_data_table_conf.xml.sample`` file

- Check your tool file with ``planemo lint``
- Run functional tool tests in a local Galaxy with ``planemo test``
- Serve the tool on a local Galaxy instance for manual verification that everything looks as expected with the ``planemo serve`` command

Uploading Your Tool
-------------------

- Ensure you have a ``.shed.yml`` file with the appropriate contents.
- Check the ``.shed.yml`` with ``planemo shed_lint``.
- Create the remote repository with ``planemo shed_create --shed_target [toolshed|your_local_shed:9000]``.

Adding Your Tool to the IUC Repository
--------------------------------------

- Create an issue on IUC GitHub tracking your progress and ensuring that no one else is working on the same tool.
- Fork IUC GitHub on your GitHub account
- Clone of the corresponding repository ``git clone https://github.com/<YOUR_NAME>/tools-iuc tools-iuc``
- Within that folder, create a corresponding branch. You might name it after the tool.
- After you have tested your tool and are completely happy with it (per
  previous sections of this document), add your tool and all associated data,
  then Commit the changes with ``git commit``
- Go to the `IUC's Repository <https://github.com/galaxyproject/tools-iuc>`__ and click on 'Compare & Pull Request'
- Add a comment describing what the tool and any extra information that might
  be needed (E.g. "I had some trouble with the data tables, can someone please
  double check them")
- The IUC will review your tool for inclusion
