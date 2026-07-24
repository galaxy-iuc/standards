Packages / Tool Dependencies
============================

Galaxy tools declare their dependencies with ``<requirement>`` elements that
Galaxy resolves at runtime. The community standard is `Conda
<https://docs.conda.io/>`__ packages from the `Bioconda
<https://bioconda.github.io/>`__ and `conda-forge <https://conda-forge.org/>`__
channels, with `BioContainers <https://biocontainers.pro/>`__ providing matching
containers automatically.

.. note::

   The older Tool Shed *tool dependency packages* (``package_*`` repositories
   containing ``tool_dependencies.xml`` with ``<action type="download_by_url">``
   directives) are **deprecated** and should not be used for new tools. Declare
   Conda requirements instead.

Declaring requirements
----------------------

Reference a Bioconda/conda-forge package by name and version, e.g.

.. code-block:: xml

    <requirements>
        <requirement type="package" version="1.2.36">aragorn</requirement>
    </requirements>

Pin the version with a ``@TOOL_VERSION@`` macro token and reuse it in the
``<requirement>`` as described in :doc:`tool_xml`.

If a package does not yet exist
-------------------------------

Search `Bioconda <https://bioconda.github.io/>`__ and `conda-forge
<https://conda-forge.org/>`__ first -- someone may already have packaged your
dependency. If not, create a recipe: the Conda recipe (``meta.yaml``) carries
the download URL and a ``sha256`` checksum, so installs are integrity-checked
and reproducible. Consider announcing your packaging effort on the
`tools-iuc Matrix channel <https://matrix.to/#/#galaxy-iuc_iuc:gitter.im>`__ so
others can help or avoid duplicating work.

Learn more
----------

The `Planemo paper <https://doi.org/10.1101/gr.276963.122>`__, particularly its
automation pipeline in Figure 2, illustrates how new upstream releases flow
through Conda packages and containers into updated Galaxy tools and workflows.

The Galaxy Training Network covers modern dependency management in depth:

- `Tool Dependencies and Conda
  <https://training.galaxyproject.org/training-material/topics/dev/tutorials/conda/slides.html>`__
  -- connecting tools to Conda/Bioconda packages
- `Prerequisites for building software / Conda packages
  <https://training.galaxyproject.org/training-material/topics/dev/tutorials/conda_sys/slides.html>`__
  -- compiling and packaging software from source
- `Tool Dependencies and Containers
  <https://training.galaxyproject.org/training-material/topics/dev/tutorials/containers/slides.html>`__
  -- BioContainers and automatic container resolution
