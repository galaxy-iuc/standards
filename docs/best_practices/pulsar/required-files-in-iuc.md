---
orphan: true
---

# Corpus Research: required_files Usage in IUC (AI Generated)

If you are adding `<required_files>` to a tool and want real exemplars to copy,
this page surveys how the [galaxyproject/tools-iuc](https://github.com/galaxyproject/tools-iuc)
collection uses the element in practice — the patterns that work, a couple that
don't, and a recommended shape for a new tool. It backs the
{doc}`Pulsar compatibility checklist <../pulsar>` and complements Galaxy's
reference docs for the
[`required_files` tool element](https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-required-files).

## What the element is for

`<required_files>` declares which files from a tool's own directory must travel
with the job when it runs somewhere other than the Galaxy server — most
importantly [remote execution via **Pulsar**](https://pulsar.readthedocs.io/),
where the tool directory is not on a shared filesystem and only the declared
files get staged to the remote host. Any wrapped script you reach for through
`$__tool_directory__` needs to be listed here, or it silently goes missing on a
Pulsar node while working fine locally.

Adoption across IUC is small but growing, and the exact set turns over fast
enough that pinning a list here would be misleading within weeks. To see who
declares it today, search the collection directly:

- [tool XMLs in tools-iuc containing `<required_files`](https://github.com/search?q=repo%3Agalaxyproject%2Ftools-iuc+%22%3Crequired_files%22&type=code)

As a snapshot: on **2026-07-27**, 23 tool wrappers declared the element. This is
nowhere near universal — the vast majority of IUC tools that call
`$__tool_directory__/script.py` still do **not** declare `required_files` and
rely on the legacy whole-directory copy. So there is not yet a deep well of
precedent, but the exemplars discussed below give you a clean set to model from.

One thing worth knowing up front: as of that snapshot every wrapper that
declares the element uses only the `<include path="..."/>` form. There is no use
of `<exclude>`, glob patterns, or bulk `directory=` inclusion anywhere in the
collection. In practice `required_files` is used purely as an explicit
allow-list of individual files — so that is the idiom to follow.

Links to tool XMLs below are pinned to a fixed commit so the line numbers keep
pointing at what the text describes; follow the search link above for the
current state of any given wrapper.

## Ways tools use it

The exemplars fall into a handful of shapes. Find the one closest to your tool
and copy it.

### A single helper or entry script — the common case

By far the most frequent pattern: one wrapper script (Python or R) lives beside
the XML and is both declared and invoked through `$__tool_directory__`.
[add_input_name_as_column](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/add_input_name_as_column/add_input_name_as_column.xml#L6)
is the canonical shape:

```xml
<required_files>
    <include path="add_input_name_as_column.py"/>
</required_files>
```

and the command simply runs
`python '$__tool_directory__/add_input_name_as_column.py'`. Other one-script
examples you can copy directly:

- [microsatbed](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/microsatbed/microsatbed.xml#L25) — `find_str.py`
- [bigwig_outlier_bed](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/bigwig_outlier_bed/bigwig_outlier_bed.xml#L23) — `bigwig_outlier_bed.py`
- [endorspy](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/endorspy/endorspy.xml#L12) — `endorS.py`
- [brew3r_r](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/brew3r_r/brew3r_r.xml#L17) — `brew3r.r_script.R`
- [vcontact2](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/vcontact2/vcontact_gene2genome.xml#L11) — `extract_p2c_mapping.py`
- [remove_terminal_stop_codons](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/remove_terminal_stop_codons/remove_terminal_stop_codons.xml#L11)
- [virAnnot_blast2tsv](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/virannot/virAnnot_blast2tsv.xml#L8) — `blast2tsv.py`

### A script in a subdirectory

Same as above, but the script lives under a `scripts/` (or similar) subdirectory.
Just write the relative path — including the subdirectory — into `path`, and
reference the same relative path under `$__tool_directory__` in the command.
[hyphy_infer_stasis_clusters](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/hyphy/hyphy_infer_stasis_clusters.xml#L11):

```xml
<required_files>
    <include path="scripts/infer_stasis_clusters.py"/>
</required_files>
```

run with `python3 '$__tool_directory__/scripts/infer_stasis_clusters.py'`. The
sibling [hyphy_strike_ambigs](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/hyphy/hyphy_strike_ambigs.xml#L7)
does the same with a HyPhy batch-language file, `scripts/strike-ambigs.bf` — a
reminder that the declared file need not be Python or R.

### Several co-dependent scripts

When the entry script imports or sources its siblings, or the pipeline shells out
to more than one file, declare them all.
[virAnnot_otu](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/virannot/virAnnot_otu.xml#L8)
is the clearest example:

```xml
<required_files>
    <include path="otu.py" />
    <include path="seek_otu.R" />
    <include path="rps2tree_html.py" />
</required_files>
```

Only `otu.py` is named on the command line; it is handed the tool directory
(`-tp '$__tool_directory__/'`) so it can locate its two helpers at runtime. Those
helpers never appear on the command line, so without the explicit includes they
would be missing on a Pulsar node. Same idea, different languages:

- [hgvsparser](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/hgvsparser/hgvsparser.xml#L11)
  declares two R files, `parseHGVS.R` and `buildHGVS.R`, each `source()`d from
  `$__tool_directory__`.
- [ena_upload](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/ena_upload/ena_upload.xml#L16)
  declares `extract_tables.py` and `dump_yaml.py`, called at different stages of
  the command.

### A library sourced by a generated config script

Sometimes the declared file is a **library** of functions rather than the entry
point: the actual program is written into a `<configfile>` at runtime, and that
generated script sources the library from `$__tool_directory__`. Both
[ggplot2_barplot](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/ggplot2/ggplot2_barplot.xml#L11)
and [ggplot2_boxplot](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/ggplot2/ggplot2_boxplot.xml#L11)
do this:

```xml
<required_files>
    <include path="utils.r" />
</required_files>
```

with the command
`Rscript -e 'source("${__tool_directory__}/utils.r")' -e 'source("${run_script}")'`
— the shared library is sourced first, then the generated `run_script` configfile.
The key point: `required_files` and `configfiles` are complementary. The stable
helper code is declared as a required file; the per-job program stays a
`<configfile>`.

### Copying files into the working directory

Occasionally the declared files are not run in place from `$__tool_directory__`
at all — the command copies them into the job working directory first. This comes
up with Python, where the caller and its imported modules must sit in the same
directory (a soft link does not satisfy the `import`).
[table_compute](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/table_compute/table_compute.xml#L100):

```xml
<required_files>
    <include path="scripts/safety.py" />
    <include path="scripts/table_compute.py" />
</required_files>
```

```bash
cp '$userconf' ./userconfig.py &&
cp '$__tool_directory__/scripts/safety.py' ./safety.py &&
cp '$__tool_directory__/scripts/table_compute.py' ./table_compute.py &&
python ./table_compute.py
```

A generated `userconfig.py` has to be importable from the same directory as the
script, so everything is copied together. Even though the scripts are copied
rather than executed in place, they still must be listed in `required_files` so
they exist on the remote host to be copied.

## Patterns worth internalizing

- **Include-only allow-list.** Every tool uses `<include path="..."/>` and
  nothing else. Treat `required_files` as "the explicit list of tool-dir files
  this job needs," never as "start from everything and subtract."
- **One include per `$__tool_directory__` reference.** The healthy idiom is 1:1 —
  every file the command reaches for under `$__tool_directory__/...` has a
  matching `<include>` with the **same relative path**. Both `$__tool_directory__/x`
  and `${__tool_directory__}/x` spellings work and are used interchangeably.
- **Relative paths mirror the on-disk layout.** Paths are always relative to the
  tool directory (`find_str.py`, `scripts/table_compute.py`); subdirectories go
  straight into the `path` attribute.
- **It's usually code.** Most declared files are executable wrappers and
  helpers — `.py`, `.R`/`.r`, one HyPhy `.bf`. Small static data shipped
  alongside the wrapper is fair game too:
  [getitd](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/getitd/getitd.xml#L7)
  declares `anno/amplicon.txt` and `anno/amplicon_kayser.tsv`. What does *not*
  belong here is bulk reference data or `.loc` files — those go through a data
  table, not the tool directory.

## Anti-patterns to avoid

- **A declared file that is never used.**
  [upsetr](https://github.com/galaxyproject/tools-iuc/blob/62fae6b29e07b58aa96af109f71ef30e8f9bc682/tools/upsetr/rcx_upsetplot.xml#L11)
  included `utils.r`, but nothing in its command or run-script configfile ever
  referenced it (the command is just `Rscript '${run_script}'`). It looks
  copy-pasted from the ggplot2 wrappers, which genuinely source `utils.r`.
  Staging it is dead weight and a maintenance trap — drop includes you don't use.
  (The wrapper has since dropped the block entirely, hence the pinned link.)
- **The entry script left off the list.**
  [extract_genomic_dna](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/extract_genomic_dna/extract_genomic_dna.xml#L8)
  declares only `extract_genomic_dna_utils.py`, but the command actually runs
  `python '$__tool_directory__/extract_genomic_dna.py'` — the main entry script is
  **not** declared. Under Pulsar, only the utils file would stage and the tool
  would fail to find its own entry point. This is the sharpest cautionary
  example: the whole value of the element is defeated if the invoked script is
  omitted.
- **Inconsistent path spellings.** Some tools write `$__tool_directory__/foo` and
  others `${__tool_directory__}/foo`. Both work; pick one for readability within
  a wrapper.

## A recommended shape for a new tool

For a typical single-script wrapper:

```xml
<required_files>
    <include path="myscript.py"/>
</required_files>
...
<command><![CDATA[
    python '$__tool_directory__/myscript.py' ...
]]></command>
```

Guidelines distilled from the healthy exemplars:

1. **List every file the command reads from `$__tool_directory__`** — the entry
   script *and* any helper or library it imports or sources. Cross-check the
   `required_files` block against every `$__tool_directory__` reference in the
   command, `version_command`, and configfiles.
   ([virAnnot_otu](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/virannot/virAnnot_otu.xml)
   and [hgvsparser](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/hgvsparser/hgvsparser.xml)
   get this right; extract_genomic_dna does not.)
2. **Don't list files you never reference** — no speculative includes (the
   upsetr mistake).
3. **Keep `path` relative and identical to the on-disk layout**, including any
   `scripts/` subdirectory (hyphy, table_compute).
4. **Include-only.** Enumerate exactly what is needed; there is no IUC precedent
   for `<exclude>` or globbing, so prefer the explicit list.
5. **Pair with `configfiles`, don't replace them.** Static helper code goes in
   `required_files`; per-job generated scripts stay as `<configfile>` (the
   ggplot2 pattern).
6. **If import-locality forces a copy into the working directory**, still declare
   the sources in `required_files` so they exist on the remote host to be copied
   (the table_compute pattern).
