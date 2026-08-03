Tool Dependencies
=================

Galaxy tools declare their dependencies with ``<requirement>`` elements that
Galaxy resolves at runtime. The community standard is `Conda
<https://docs.conda.io/>`__ packages from the `Bioconda
<https://bioconda.github.io/>`__ and `conda-forge <https://conda-forge.org/>`__
channels, with `BioContainers <https://biocontainers.pro/>`__ providing matching
containers automatically.

Declaring requirements
----------------------

Reference a Bioconda/conda-forge package by name and version, e.g.

.. code-block:: xml

    <requirements>
        <requirement type="package" version="1.2.36">aragorn</requirement>
    </requirements>

If the Galaxy tool is a wrapper for an underlying tool, pin the version with a
``@TOOL_VERSION@`` macro token and reuse it in the ``<requirement>`` as
described in :doc:`tool_xml`.

If a package does not yet exist
-------------------------------

Search `Bioconda <https://bioconda.github.io/>`__ and `conda-forge
<https://conda-forge.org/>`__ first -- someone may already have packaged your
dependency. If not, create a recipe: the Conda recipe (``meta.yaml``) carries
the download URL and a ``sha256`` checksum, so installs are integrity-checked
and reproducible. Consider announcing your packaging effort on the
`Bioconda Matrix channel <https://matrix.to/#/#bioconda_Lobby:gitter.im>`__ so
others can help or avoid duplicating work. For Galaxy wrapper questions, use the
`tools-iuc Matrix channel <https://matrix.to/#/#galaxy-iuc_iuc:gitter.im>`__.

Multi-requirement containers
----------------------------

A tool with a single requirement gets its BioContainer automatically. Tools that
combine *multiple* requirements need a "mulled" container bundling that specific
combination, and those are not built until the combination has been registered.

The `planemo-monitor <https://github.com/galaxyproject/planemo-monitor>`__
repository automates that registration on behalf of the community. A scheduled
GitHub Actions workflow (`monitor.yaml
<https://github.com/galaxyproject/planemo-monitor/blob/master/.github/workflows/monitor.yaml>`__)
runs once a day. For every repository it tracks, it runs
``planemo container_register --recursive`` on it, which walks all of the tools,
collects each multi-requirement combination, and - for any combination not
already published or already pending - opens a pull request against
`BioContainers/multi-package-containers
<https://github.com/BioContainers/multi-package-containers>`__. Once that pull
request is merged, the multi-package-containers CI builds the mulled container
and publishes it to quay.io, from where Galaxy can pull it to execute the tool
in a container.

To have your own tools covered, add your repository's clone URL to one of the
``repositories*.list`` files in planemo-monitor via a pull request. From then on
your multi-requirement tools will have their containers registered and built
automatically, with no further action required on your part.

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

.. note::

   The older Tool Shed *tool dependency packages* (``package_*`` repositories
   containing ``tool_dependencies.xml`` with ``<action type="download_by_url">``
   directives) are **deprecated** and should not be used for new tools. Declare
   Conda requirements instead.