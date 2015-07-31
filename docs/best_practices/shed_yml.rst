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

Advanced Parameters
-------------------

    Currently there exists a tension between what is best for developers (storing all tools in a
    single repository - e.g. ``ncbi_blast_plus`` or ``bedtools``) and what is best for Galaxy users (storing
    a single repository per tool and collecting them together with a suite - e.g. ``samtools`` or ``gatk``).

Thus a number of advanced parameters were added for helping developers manage suites of tools.

.. code:: yaml

    auto_tool_repositories:
      name_template: "{{ tool_id }}"
      description_template: "Wrapper for samtools application {{ tool_name }}."
    suite:
      name: "suite_samtools_1_2"
      description: "A suite of Galaxy tools designed to work with version 1.2 of the SAMtools package."
      long_description:
      > SAM (Sequence Alignment/Map) format is a generic format for storing large nucleotide sequence
        alignments.   This repository suite associates selected repositories containing Galaxy utilities that require
        version 1.2 of the SAMTools package.  These associated Galaxy utilities consist of a Galaxy Data
        Manager contained in the repository named data_manager_sam_fasta_index_builder and Galaxy tools
        contained in several separate repositories.

This example assumes the ``.shed.yml`` file is placed in a "flat" directory with each samtools tool
wrapper. Planemo will create and update repositories for each individual tool given the specified
templates in auto_tool_repositories. The suite key here will auto-generate a suite repository for
all of these tools and will automatically created the corresponding repository_dependencies.xml to
populate it with (this is generated during shed_upload and never needs to exist in your repository).

Again this example is admittedly idealized, but if ``auto_tool_repositories`` is
not specified, a repositories list can be specified instead. There are some
examples of this in the planemo's test data:

-  `This .shed.yml <https://github.com/galaxyproject/planemo/blob/master/tests/data/repos/multi_repos_flat_configured/.shed.yml>`__
   is a simple example of specifying custom repositories for individual tools.
-  `This <https://github.com/galaxyproject/planemo/blob/master/tests/data/repos/multi_repos_flat_configured_complex/.shed.yml>`__
   demonstrates complex inclusions files from sub-directories and renaming.

The test data also includes some more advanced usages of the suite key as well - specifically using
it without `auto_tool_repositories <https://github.com/galaxyproject/planemo/blob/master/tests/data/repos/suite_auto/.shed.yml>`__ 
as a generic replacement for repository_dependencies.xml and adding `additional dependent
repositories <https://github.com/galaxyproejct/planemo/blob/master/tests/data/repos/multi_repos_flat_flag_suite/.shed.yml>`__
in addition to the ones defined by the .shed.yml file.


Shed Upload Includes/Excludes
-----------------------------

Sometimes it is of interest to have shared data in a single directory, and then to ``include`` that
when needed. A good example of this are the `blast <https://github.com/peterjc/galaxy_blast/blob/master/tools/ncbi_blast_plus/.shed.yml>`__
wrappers which take advantage of the feature in order to share test data amongst a number of
directories which all need the data.

.. code:: yaml

    include:
    - strip_components: 2
      source:
      - ../../test-data/blastdb.loc
      - ../../test-data/blastdb_d.loc
      - ../../test-data/blastdb_p.loc
      - ../../test-data/blastn_arabidopsis.extended.tabular

This snippet informs planemo that it should include specific datasets from ``../../test-data`` and
that as part of the include process it should strip the first two path components.

The ``ignore`` or ``exclude`` functionality works similarly, just specify a list of paths you wish
to exclude:

.. code:: yaml

    exclude:
      - test-data/my-gigantic-test-dataset.fastq

