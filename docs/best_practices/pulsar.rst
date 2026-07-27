Remote Execution Checklist
==========================

`Pulsar <https://pulsar.readthedocs.io/>`__ runs Galaxy jobs on a remote
compute resource that does **not** share a filesystem with the Galaxy server.
Most tools "just work", but a handful of authoring habits quietly assume that
the server's filesystem is the job's filesystem — and those break only when the
tool is finally run through Pulsar on a production Galaxy server.

The unifying principle behind every item below:

    The Cheetah ``<command>`` template and job setup are evaluated on the
    Galaxy **head node**, but the job runs on a **remote filesystem** with
    different paths and a possibly empty view of the tool directory, reference
    data, and outputs. Assume nothing about shared paths.

The Checklist
-------------

#. :ref:`Declare every tool-directory file with \<required_files\> <pulsar-required-files>`
   — anything sourced, imported, or copied in, the entry script itself, and not
   just what is named on the command line.
#. :ref:`No filesystem I/O in Cheetah templates <pulsar-no-fs-io>`
   — use dataset metadata, never ``os.path``/``open`` on data paths.
#. :ref:`Do not reach into $__app__ at template time <pulsar-data-tables>`
   — discouraged for tools generally; use ``from_data_table`` + ``.fields.path`` for reference data.
#. :ref:`No hardcoded absolute paths <pulsar-no-abs-paths>`
   — to reference data, indexes, scratch, or ``/tmp``.
#. :ref:`Outputs must be real files inside the job output directory <pulsar-outputs-in-jobdir>`
   — never symlink an output to an input or outside the job tree.
#. :ref:`Keep discovered outputs inside the job working directory <pulsar-discovered-outputs>`
   — ``discover_datasets`` / ``from_work_dir`` / collection discovery stage back only from the job tree.

Details
-------

.. _pulsar-required-files:

1. Declare every tool-directory file with ``<required_files>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pulsar stages a tool's own files to the remote node only if it can determine
they are needed. Historically it inferred this from the command line: a helper
named directly in ``<command>`` (``python '$__tool_directory__/foo.py'``) gets
transferred, but a file pulled in *indirectly* — ``source()``\ d, ``import``\ ed,
or ``include``\ d by another script — is invisible to that scan and is missing
on the node. The symptom is always ``No such file or directory`` / ``can't stat``
at job runtime.

Declare such files explicitly so staging is deterministic and author-controlled.
This matters most when a file is *not* named on the command line.

A Python tool that shells out to helper scripts (`virAnnot_otu
<https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/virannot/virAnnot_otu.xml>`__)
runs ``python '$__tool_directory__/otu.py' … -tp '$__tool_directory__/'`` but
reaches its helpers at runtime with
``os.path.join(tool_path, 'seek_otu.R')`` and ``os.path.join(tool_path, 'rps2tree_html.py')`` —
so those two never appear on the command line and all three files must be
declared:

.. code-block:: xml

    <required_files>
        <include path="otu.py" />
        <include path="seek_otu.R" />
        <include path="rps2tree_html.py" />
    </required_files>

An R tool that sources a shared utility library (`ggplot2_barplot
<https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/ggplot2/ggplot2_barplot.xml>`__)
runs ``Rscript -e 'source("${__tool_directory__}/utils.r")' -e 'source("${run_script}")'``.
Here ``utils.r`` holds shared helper functions (``load_data()`` and friends) while
the analysis itself is a generated ``run_script`` configfile — so the sourced
library must be declared:

.. code-block:: xml

    <required_files>
        <include path="utils.r" />
    </required_files>

.. _pulsar-required-files-correct:

**Getting the declaration right.** Most real-world failures are not a missing
block — they are a subtly incomplete one:

- **Declare the entry script too**, not only its helpers. Some tools declare a
  ``_utils.py`` but not the main script that ``$__tool_directory__`` runs.
- **Use the correct relative path** (relative to the tool directory). A file
  declared at the wrong location stages nothing.
- **Declare files you copy into the working directory** (``cp
  '$__tool_directory__/x' .``), not only the ones you execute directly.
- **Drop dead includes** — a declared file that is never referenced is just
  staging overhead and a maintenance trap.

For example, `table_compute
<https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/table_compute/table_compute.xml>`__
copies its scripts into the working directory (a soft link does not satisfy a
Python ``import``), so *both* copied files must be declared even though only one
is invoked directly:

.. code-block:: xml

    <required_files>
        <include path="scripts/safety.py" />
        <include path="scripts/table_compute.py" />
    </required_files>

.. code-block:: shell

    cp '$__tool_directory__/scripts/safety.py' ./safety.py &&
    cp '$__tool_directory__/scripts/table_compute.py' ./table_compute.py &&
    python ./table_compute.py

.. _pulsar-no-fs-io:

2. No filesystem I/O in Cheetah templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The template runs on the Galaxy server, so opening or stat-ing a data file by
path uses the *server's* path — which is wrong or nonexistent when the
destination is Pulsar. At template time ``$input`` is a remote path string; do
not feed it to Python file I/O.

.. code-block:: none

    ## WRONG — raises on the server; the path is remote
    #set size = $os.path.getsize(str($in_file))

    ## RIGHT — metadata Galaxy already knows, no filesystem access
    #set size = $in_file.get_size()

Use dataset metadata (``.get_size()``, ``.metadata.*``, ``.element_identifier``,
``.is_of_type(...)``) instead of ``open`` / ``os.path`` / ``os.stat`` /
``os.listdir`` on data paths.

**When metadata is not enough, defer to runtime.** Sometimes you genuinely need
to list a directory, glob a set of produced files, or read a file's contents —
metadata cannot answer that. The fix is *not* to do it in the template; it is to
do it in the part of the job that runs **on the node**, where the files actually
exist. The shell ``<command>`` body and any ``<configfile>`` script execute
remotely, so the very call that is fatal in a Cheetah ``#set`` is correct there.

The cleanest contrast is a Python glob. In a Cheetah template it stats the
server's filesystem and breaks under Pulsar; moved into a ``<configfile>`` (as in
`snapatac2
<https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/snapatac2/dimension_reduction_clustering.xml>`__)
the identical code runs on the node against files that are really present:

.. code-block:: python

    ## In a <configfile> — runs on the node, the files exist here
    import glob
    files = sorted(glob.glob('adata_*.h5ad'))

Only the *rendered* content runs remotely: a ``<configfile>`` is still
Cheetah-rendered on the Galaxy server before it is staged. ``import glob`` above
is plain text that Cheetah passes through, but ``#set files = os.listdir(...)``
in the same file is a Cheetah directive and still runs on the head node.

Equivalently, let the job shell expand the glob rather than listing directories
at template time (`prinseq
<https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/prinseq/prinseq.xml>`__,
`macs2
<https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/macs2/macs2_callpeak.xml>`__):

.. code-block:: shell

    ## enumerate outputs on the node — never os.listdir() on the head node
    for f in tmp/*.fastq; do gzip -c "$f" > tmp_file && mv tmp_file "$f"; done

.. _pulsar-data-tables:

3. Do not reach into ``$__app__`` at template time
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``$__app__`` exposes Galaxy's live internal application object inside the
Cheetah template. Reaching into it is discouraged as a general tool-authoring
practice — independent of Pulsar — because it couples the tool to Galaxy's
runtime internals and server-specific configuration: it sidesteps the parameter
machinery, is not portable or reproducible across servers, and rides on internal
APIs that are not part of the stable tool contract. A well-behaved tool's
command line should be a function of its *declared inputs*, not of server state.

One ``$__app__`` paradigm is especially toxic for Pulsar. Reaching into
``$__app__.tool_data_tables[...].get_fields()`` and materializing a path in the
template bakes a *server-side* absolute path into the command line — which
Pulsar will not rewrite, so the job fails on a node that has a different (or no)
view of that path. Let Galaxy resolve the path through normal, Pulsar-aware
handling instead:

.. code-block:: xml

    <param name="reference" type="select" label="Reference genome">
        <options from_data_table="my_index" />
    </param>

and reference ``$reference.fields.path`` directly on the command line — do not
``str()``-materialize it into an intermediate ``#set``.

.. _pulsar-no-abs-paths:

4. No hardcoded absolute paths
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Absolute paths to reference data, indexes, scratch, or ``/tmp`` will not exist
on the remote node and will not be rewritten. Route reference data through a
data table so the path is a rewritable handle rather than a literal.

Whether that data is actually *present* on the compute node (typically via
CVMFS or a shared mount) is a deployment concern for the Pulsar operator, not a
tool-XML bug — but the tool's part of the bargain is to never bake in an
absolute path.

.. _pulsar-outputs-in-jobdir:

5. Outputs must be real files inside the job output directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every output — including composite datasets and ``extra_files_path`` contents —
must be a real file written inside the job's output directory. Never
``ln -s`` an output (or an entry in its files-path) to an input dataset, a
reference path, or anything outside the job working directory.

Pulsar's staging guard rejects a path that resolves outside the authorized job
directory, and the symlink is fragile even locally — it dangles as soon as the
input dataset is purged or moved. Remote execution simply surfaces a latent bug.

.. _pulsar-discovered-outputs:

6. Keep discovered outputs inside the job working directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The same principle as item 5, seen from the discovery angle.
``discover_datasets``, ``from_work_dir``, and ``<collection>`` discovery all
stage results back reliably **provided the files land inside the job working
directory** (or a ``directory=`` subdirectory under it). Outputs written to an
absolute path or outside the job tree are never staged back, by design.
