---
orphan: true
---

# Corpus Research: Pulsar Compatibility Issues (AI Generated)

If you write Galaxy tools, sooner or later one of them will be run through
[Pulsar](https://pulsar.readthedocs.io/) on a remote compute resource that does
**not** share a filesystem with the Galaxy server. Most tools just work. The
ones that don't tend to fail in a small number of recognizable ways — and
almost always for the same underlying reason:

> The Cheetah `<command>` template and job setup are evaluated on the Galaxy
> **head node**, but the job runs on a **remote filesystem** with different
> paths and a possibly empty view of the tool directory, reference data, and
> outputs. Anything that assumes "the server's filesystem is the job's
> filesystem" breaks under Pulsar.

This page catalogs the failure modes that real tools in
[`galaxyproject/tools-iuc`](https://github.com/galaxyproject/tools-iuc) have hit,
organized so you can recognize the shape of a problem in your own tool before a
user files the bug. Each category links the issues and pull requests where the
problem was diagnosed and fixed. It backs the main
{doc}`Remote Execution Checklist <../pulsar>`.

## Category A — Tool-directory files that never reach the remote node

This is the single most common class of failure. Pulsar stages a tool's own
scripts to the remote node only if it can figure out they're needed. Historically
it inferred that from the command line: a helper named directly in `<command>`
(e.g. `python '$__tool_directory__/foo.py'`) gets transferred, but a script
pulled in *indirectly* — sourced, imported, or included by another script, or
referenced only at runtime — is invisible to that inference and simply isn't
there when the job runs. The symptom is always a `No such file or directory` or
`can't stat` error at job runtime.

The classic example is
[deseq2](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/deseq2/deseq2.xml):
its `get_deseq_dataset.R` is `source()`d by `deseq2.R` but never named in the
tool XML, so Pulsar didn't transfer it and the job failed
([#2467](https://github.com/galaxyproject/tools-iuc/issues/2467)). The original
fix ([#3420](https://github.com/galaxyproject/tools-iuc/pull/3420)) reached for a
well-known hack — `touch '${__tool_directory__}/get_deseq_dataset.R' &&` at the
top of `<command>` to trick Pulsar's command-line scan into staging the include.
That thread explicitly calls it "a terrible hack" and asks for a real mechanism,
which became `<required_files>`.

The same shape recurs whenever a script imports a helper module that isn't on the
command line:

- [table_compute](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/table_compute/table_compute.xml)
  failed with `cp: can't stat '.../tool_files/scripts/safety.py'` because
  `table_compute.py` imports `safety.py`. Fixed by declaring the import in
  `<required_files>` ([#6759](https://github.com/galaxyproject/tools-iuc/pull/6759),
  later corrected in [#7040](https://github.com/galaxyproject/tools-iuc/pull/7040)).
- [Extract Genomic DNA](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/extract_genomic_dna/extract_genomic_dna.xml)
  needed its imported `extract_genomic_dna_utils.py` module declared
  ([#6580](https://github.com/galaxyproject/tools-iuc/pull/6580)).
- [Add input name as column](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/add_input_name_as_column/add_input_name_as_column.xml)
  needed `add_input_name_as_column.py` declared
  ([#7264](https://github.com/galaxyproject/tools-iuc/pull/7264)).
- The [hyphy](https://github.com/galaxyproject/tools-iuc/tree/main/tools/hyphy)
  tools had a `<required_files>` block, but the `<include>` pointed at the *wrong*
  relative path — the file was declared yet staged nothing
  ([#7780](https://github.com/galaxyproject/tools-iuc/pull/7780)).

This is exactly the class that `<required_files>` was designed to fix. See
{ref}`checklist item 1 <pulsar-required-files>` for how to declare these files
completely and correctly.

**The Galaxy tool linter now catches this.** It flags files referenced via
`$__tool_directory__` that aren't declared in `<required_files>`, and IUC CI runs
a remote-simulation lint. A tool that legitimately needs to suppress a specific
false positive can use a per-tool `.lint_skip` file — as in
[staramr](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/staramr/staramr_search.xml),
where a forgotten skip entry had to be restored
([#7942](https://github.com/galaxyproject/tools-iuc/pull/7942)).

## Category B — Filesystem operations inside the Cheetah template

Because the template runs on the Galaxy server, any attempt to *open or stat the
actual data file by path* uses the server's path — which is wrong, or simply
doesn't exist, when the job is destined for Pulsar. At template time the value of
`$input` is just a remote path string; feeding it to Python file I/O blows up
during job preparation, before the job ever reaches the node.

The
[datamash transpose](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/datamash/datamash-transpose.xml)
tool did exactly this: an `os.path.getsize(str($in_file))` call in Cheetah raised
because `$in_file` is a remote path the server can't see, killing the job in
`__prepare_job` ([#5621](https://github.com/galaxyproject/tools-iuc/issues/5621)).
The fix ([#5623](https://github.com/galaxyproject/tools-iuc/pull/5623)) swapped it
for the metadata accessor `$in_file.get_size()`, a value Galaxy already knows
without touching any filesystem. The PR author's takeaway is worth memorizing:
*"You can never open files in cheetah templates."*

**The rule:** use dataset metadata (`.get_size()`, `.metadata.*`,
`.element_identifier`) instead of `os` / `open` / `os.path` on data paths. When
you genuinely need to glob or list files, do it in the part of the job that runs
*on the node* (the shell `<command>` body or a `<configfile>`), not in the
template.

## Category C — Resolving tool-data tables at template time via `$__app__`

This is Category B's cousin, specific to reference-data lookups. Reaching into
`$__app__.tool_data_tables[...].get_fields()` and manually resolving a filesystem
path inside the template bakes a *server-side* absolute path into the command
line — one that Pulsar won't rewrite, so the job fails on a node with a different
(or nonexistent) view of that path.

- [vsnp](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/vsnp/vsnp_get_snps.xml)
  replaced a template-time `$__app__.tool_data_tables['vsnp_excel'].get_fields()`
  loop with an ordinary `<param type="select" ... from_data_table>` whose
  `.fields.path` Galaxy resolves through its normal, Pulsar-aware handling
  ([#4488](https://github.com/galaxyproject/tools-iuc/pull/4488)).
- [malt_run](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/malt/malt_run.xml)
  removed an intermediate `#set ref = str($reference.fields.path)` and used
  `$reference.fields.path` directly on the command line — the `str()`-materialized
  path had short-circuited normal path handling
  ([#4499](https://github.com/galaxyproject/tools-iuc/pull/4499)).

Route reference data through a
[`from_data_table` select parameter](https://docs.galaxyproject.org/en/latest/dev/schema.html)
and reference `.fields.path` directly. Don't reach into `$__app__`, and don't
`str()`-materialize a path field into an intermediate `#set`.

## Category D — Composite datasets, extra-files paths, and symlinks

Composite and `extra_files_path` outputs have to be staged back file by file, and
symlinks that point *outside* the job directory both fail Pulsar's security
boundary and break the moment the job moves to another host.

The snpEff `snpEff_build_gb` tool symlinked `sequences.fa` / `genes.gtf` in its
output files-path to input datasets living outside `outputs/`, and Pulsar's path
guard (correctly) refused to stage them —
`Attempt to read or write file outside an authorized directory`
([#5647](https://github.com/galaxyproject/tools-iuc/issues/5647)). The diagnosis
in that thread is instructive: those symlinks would dangle off-Pulsar too, and
only the `*.bin` file was actually needed. Remote execution simply surfaced a
latent bug. Write real files into the output's files-path; never symlink an
output to an input or to anything outside the job directory.

## Category E — Reference/index data availability on the compute node

Even a perfectly written tool needs its reference and index data present where
the job actually runs. Data-table paths that resolve on the head node — often via
CVMFS or a shared `tool-data` mount — must also be mounted or rewritten on the
Pulsar node. This is largely a **deployment** concern for the Pulsar operator
rather than a tool-XML bug, but it shows up as "index not found" style failures,
and it shapes how tools should reference data: always through data tables and
`.fields.path` (a rewritable handle), never a hardcoded absolute path. No single
IUC pull request "fixes" this, because the fix lives in Pulsar / destination
configuration and CVMFS availability — but the tool author's half of the bargain
is to never bake in an absolute path.

## The unifying lesson

Every category above is a special case of one habit: **prefer dataset metadata
and Galaxy-provided handles over the filesystem, everywhere.** The template runs
on the head node and the job runs elsewhere, so assume nothing about shared
paths. Declare every tool-dir file, keep filesystem access on the node, route
reference data through data tables, keep outputs inside the job directory, and
test against a Pulsar (or Pulsar-simulating) destination before you ship. The
{doc}`Remote Execution Checklist <../pulsar>` turns these into six concrete
items.
