Toolshed Yaml File
==================

The ``.shed.yml`` file provides a way for developers using the awesome `planemo
<https://github.com/galaxyproject/planemo/>`__ to easily push their tools to
toolshed repositories.

.. code:: yaml
    
    name: package_aragorn_1_2_36
    owner: iuc
    description: Contains a tool dependency definition that downloads and extract version
      1.2.36 of Aragorn.
    homepage_url: http://mbio-serv2.mbioekol.lu.se/ARAGORN/
    long_description: |
        ARAGORN, tRNA (and tmRNA) detection.

        http://www.ncbi.nlm.nih.gov/pubmed/14704338
    remote_repository_url: https://github.com/galaxyproject/tools-iuc/tree/master/packages/package_aragorn_1_2_36
    type: tool_dependency_definition
    categories:
    - Tool Dependency Packages


+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Parameter             | Value                                                                                                                                                                                      |
+=======================+============================================================================================================================================================================================+
| name                  | This is the package or tool's name. It is usually the name of the folder that contains the ``.shed.yml`` file. This should be package_$name_$version for packages, and $name for tools     |
+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| owner                 | Your toolshed username                                                                                                                                                                     |
+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| description           | A short description of the package or tool set                                                                                                                                             |
+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| homepage_url          | This value is currently under debate, but we recommend reading over `#1 <https://github.com/galaxy-iuc/standards/issues/1>`__.                                                             |
+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| long_description      | A longer README type description of the package, as tool dependencies do no currently support README files.                                                                                |
+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| remote_repository_url | This should be the path to the folder in your github repository, on the branch you create releases from (usually master). This will eventually be used with the toolshed for update hooks. |
+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| type                  | The repository type, one of ``unrestricted``, ``tool_dependency_definition``, or ``repository_suite_definition``                                                                           |
+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| categories            | Toolshed categories that are relevant to the tool or package.                                                                                                                              |
+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

A note on the ``name`` attribute: as periods are disallowed in repository names, we recommend replacing periods in the version number with underscores.

+-----------------------+-----------------------------+-----------------------------+
| Repository Type       | Recommended Name            | Examples                    |
+=======================+=============================+=============================+
| Data Managers         | ``data_manager_$name``      | ``data_manager_bowtie2``    |
+-----------------------+-----------------------------+-----------------------------+
| Packages              | ``package_$name_$version``  | ``package_aragorn_1_2_36``  |
+-----------------------+-----------------------------+-----------------------------+
| Tool Suites           | ``suite_$name``             | ``suite_samtools``          |
+-----------------------+-----------------------------+-----------------------------+
| Tools                 | ``$name``                   | ``stringtie``, ``bedtools`` |
+-----------------------+-----------------------------+-----------------------------+
