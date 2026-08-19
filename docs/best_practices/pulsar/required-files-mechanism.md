---
orphan: true
---

# Corpus Research: required_files Mechanism (AI Generated)

This is a deep-dive companion to the {doc}`Remote Execution Checklist <../pulsar>`.
It explains what the tool-XML `<required_files>` block actually does once Galaxy and
[Pulsar](https://pulsar.readthedocs.io/) get hold of it — useful if you want to understand
*why* declaring your tool-directory files makes remote jobs reliable, and what happens when
you leave the block out.

The feature was introduced in
[galaxyproject/galaxy#12250](https://github.com/galaxyproject/galaxy/pull/12250) —
*"Systematic handling of remotely required tool files"* — merged into the **21.09** release.
It closed [pulsar#113](https://github.com/galaxyproject/pulsar/issues/113) and superseded an
earlier approach in [pulsar#260](https://github.com/galaxyproject/pulsar/pull/260). The change
touched the tool parser, the [XSD schema](https://github.com/galaxyproject/galaxy/blob/fdf016e6f90f68924b7dc9d2d5d193a52ed923de/lib/galaxy/tool_util/xsd/galaxy.xsd),
the Galaxy → Pulsar job runner, and unit tests (+353 / -3), and required a matching bump of the
Pulsar client library Galaxy depends on so it would understand the new job-description field.

The reference documentation for the element lives in the Galaxy tool-XML schema docs:
[`required_files`](https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-required-files)
and its [`include`](https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-required-files-include)
/ [`exclude`](https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-required-files-exclude)
children.

## What the feature is

`<required_files>` is a top-level tool-XML block that lets you **explicitly declare which files in
the tool's directory must be shipped to a remote host** for the job to run. It replaces a fragile
heuristic (the "Pulsar hack") that guessed at required files by scanning the rendered command line
for path-like strings.

### XML syntax

```xml
<tool id="my_tool" name="My Tool" version="1.0">
  <requirements><!-- ... --></requirements>
  <required_files>
    <include path="my_script.R" />
    <include path="scripts/" type="prefix" />
    <exclude path="scripts/experimental.R" />
  </required_files>
  <!-- command, inputs, outputs ... -->
</tool>
```

- `<required_files>` sits between `<requirements>` and `<entry_points>` in tool document order.
- It contains an ordered sequence of `<include>` elements followed by `<exclude>` elements — all
  includes should be listed before excludes.
- Each `<include>` / `<exclude>` has:
  - `path` — a path **relative to the tool's directory** (the directory containing the tool's
    `.xml` file, which is not necessarily the repository root).
  - `type` — how `path` is matched: one of `literal` (default), `prefix`, `glob`, or `regex`.
- `<required_files>` carries one attribute, `extend_default_excludes` (boolean, default `true`),
  which controls whether the built-in excludes (`tool-data`, `test-data`, `.hg`) are appended.

### `type` (path-match) semantics

| `type`    | Match rule (relative path vs. `path`)   | Implementation |
|-----------|-----------------------------------------|----------------|
| `literal` | exact string equality (default)         | `rel_path == path` |
| `prefix`  | path starts with the string             | `rel_path.startswith(path)` |
| `glob`    | shell-style wildcard match              | `fnmatch.fnmatch(rel_path, path)` |
| `regex`   | Python `re.match` (anchored at start)   | `re.match(path, rel_path)` |

The schema itself spells out the intent:

> This declaration is used to define files that must be shipped from the tool directory for the tool
> to function properly in remote environments where the tool directory is not available to the job.
> … Pulsar hacks to implicitly find referenced files from the tool directory will be disabled when
> this block is used. A future Galaxy tool profile version may disable these hacks altogether and
> specifying this block for all referenced files should be considered a best practice.

## How it's implemented in Galaxy

### The `RequiredFiles` domain object

The PR introduced a `RequiredFiles` class in
[`tool_util/parser/interface.py`](https://github.com/galaxyproject/galaxy/blob/fdf016e6f90f68924b7dc9d2d5d193a52ed923de/lib/galaxy/tool_util/parser/interface.py).
It holds `includes`, `excludes`, and `extend_default_excludes`, and its core method resolves the
declaration against a real directory:

```python
def find_required_files(self, tool_directory: str) -> List[str]:
    def matches(ie_list, rel_path):
        for ie_item in ie_list:
            ie_item_path = ie_item["path"]
            ie_item_type = ie_item.get("path_type", "literal")
            if ie_item_type == "literal":
                if rel_path == ie_item_path: return True
            elif ie_item_type == "prefix":
                if rel_path.startswith(ie_item_path): return True
            elif ie_item_type == "glob":
                if fnmatch.fnmatch(rel_path, ie_item_path): return True
            else:  # regex
                if re.match(ie_item_path, rel_path) is not None: return True
        return False

    excludes = self.excludes
    if self.extend_default_excludes:
        excludes.append({"path": "tool-data", "path_type": "prefix"})
        excludes.append({"path": "test-data", "path_type": "prefix"})
        excludes.append({"path": ".hg", "path_type": "prefix"})

    files = []
    for (dirpath, _, filenames) in safe_walk(tool_directory):
        for filename in filenames:
            rel_path = join(dirpath, filename).replace(tool_directory + os.path.sep, '')
            if matches(self.includes, rel_path) and not matches(self.excludes, rel_path):
                files.append(rel_path)
    return files
```

A few things worth knowing as an author:

- It **walks the whole tool directory** (using a symlink-safe walk that stays inside the directory)
  and returns every relative path that matches an include and does not match an exclude.
- When `extend_default_excludes` is true, the default excludes `tool-data/*`, `test-data/*`, and
  `.hg/*` are always appended — reference data, test data, and Mercurial internals should never be
  shipped to a compute node.
- Because the class lives in `galaxy.tool_util.parser`, it ships in the standalone `galaxy-tool-util`
  package and can be imported by Pulsar without pulling in the full Galaxy application. Galaxy core
  and Pulsar run the *same* resolution code.

### Parsing the XML

An abstract hook `parse_required_files() -> Optional[RequiredFiles]` was added to the `ToolSource`
interface, returning `None` by default so tools without the block fall back to the implicit logic.
The XML implementation lives in
[`tool_util/parser/xml.py`](https://github.com/galaxyproject/galaxy/blob/fdf016e6f90f68924b7dc9d2d5d193a52ed923de/lib/galaxy/tool_util/parser/xml.py).
One gotcha to note: the XML attribute `type` is normalized to the internal dict key `path_type`.

### Wiring into the `Tool` object and implicit defaults

During `Tool.parse`, in
[`galaxy/tools/__init__.py`](https://github.com/galaxyproject/galaxy/blob/fdf016e6f90f68924b7dc9d2d5d193a52ed923de/lib/galaxy/tools/__init__.py),
Galaxy resolves the tool's `required_files`, falling back to a curated table when the tool declares
nothing:

```python
required_files = tool_source.parse_required_files()
if required_files is None:
    old_id = self.old_id
    if old_id in IMPLICITLY_REQUIRED_TOOL_FILES:
        lineage_requirement = IMPLICITLY_REQUIRED_TOOL_FILES[old_id]
        lineage_requirement_until = lineage_requirement.get("version")
        if lineage_requirement_until is None or self.version_object < lineage_requirement_until:
            required_files = RequiredFiles.from_dict(lineage_requirement["required"])
self.required_files = required_files
```

`IMPLICITLY_REQUIRED_TOOL_FILES` is a **hardcoded registry of legacy tools** that reference files at
runtime but predate the `<required_files>` block — so they keep working under Pulsar without editing
their (often shed-installed, version-frozen) XML. Each entry maps a tool's `old_id` to a
`RequiredFiles`-shaped dict, optionally gated by a maximum `version` so the implicit default only
applies to versions *older* than the one that added an explicit block.

The registry shipped with a single entry —
[`deseq2`](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/deseq2/deseq2.xml) below
`2.11.40.6`, requiring `*.R` — and had grown to 16 entries as of 2026-07. It uses two convenient
shapes: `REQUIRE_FULL_DIRECTORY` (an `**` glob that ships everything, used by e.g.
[`circos`](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/circos/circos.xml)) and
per-tool globs like `{"path": "utils/*", "path_type": "glob"}`. Adding an entry here — rather than
patching frozen shed XML — is the intended maintenance path when a legacy tool is found to break
under Pulsar.

### Handoff to the Pulsar runner

The [Pulsar job runner](https://github.com/galaxyproject/galaxy/blob/fdf016e6f90f68924b7dc9d2d5d193a52ed923de/lib/galaxy/jobs/runners/pulsar.py)
reads `job_wrapper.tool.required_files` and passes it straight into the client job description
submitted to Pulsar:

```python
tool_directory_required_files = job_wrapper.tool.required_files
client_job_description = ClientJobDescription(
    ...
    tool_directory_required_files=tool_directory_required_files,
)
```

So the *resolved `RequiredFiles` object itself* (not a pre-computed file list) crosses from Galaxy
into the Pulsar client, which runs `find_required_files` against the real on-disk tool directory
during staging.

## Why it matters for remote execution

### The staging problem

Pulsar runs Galaxy jobs on a **remote host that does not share Galaxy's filesystem**. Before a job
runs, Pulsar must copy ("stage up") everything it needs: input datasets, config files, and —
critically — **files from the tool's own installation directory** that the command line invokes
(wrapper scripts, R/Python helpers, config templates, `utils/` modules, and so on). Galaxy exposes
the tool directory to the command template as `$__tool_directory__`. On a shared filesystem that
path just works; on a remote node those files are absent unless Pulsar ships them.

### The legacy "hack" this replaces

Before this PR, Pulsar guessed the tool files by scanning job inputs (the rendered command line and
config files) for substrings that *looked like* paths under the tool directory. That logic still
exists as the fallback branch in Pulsar's
[`client/staging/up.py`](https://github.com/galaxyproject/pulsar/blob/b3a2c228772272da73d107413445e170619c032b/pulsar/client/staging/up.py):
`JobInputs.find_referenced_subfiles` builds a regex and returns every path-like token it finds in
the command line and config contents.

This is brittle:

- It only finds files whose **full path literally appears** in the command string. A script that is
  invoked but whose path is assembled at runtime, or that is referenced only from *another* script,
  is missed — the job then fails on the remote host with a missing-file error (the class of bug
  behind [pulsar#113](https://github.com/galaxyproject/pulsar/issues/113)).
- It can over-match (grabbing unrelated path-like tokens) or mis-tokenize paths with spaces or
  quotes.
- It gives you no control — no way to add a file the heuristic can't see, or exclude a large
  reference-data tree it wrongly grabs.

### How `required_files` plugs into staging

`ClientJobDescription` gained a `tool_directory_required_files` field (defined in Pulsar's
[`client/staging/__init__.py`](https://github.com/galaxyproject/pulsar/blob/b3a2c228772272da73d107413445e170619c032b/pulsar/client/staging/__init__.py))
carrying the `RequiredFiles` object. During stage-up, `FileStager.__initialize_referenced_tool_files`
branches on it:

```python
def __initialize_referenced_tool_files(self):
    if self.tool_directory_required_files:
        self.referenced_tool_files = [
            (join(self.tool_dir, x), x)
            for x in self.tool_directory_required_files.find_required_files(self.tool_dir)
        ]
    else:
        # legacy heuristic fallback: scan command line / configs for path-like tokens
        ...
```

When an explicit (or implicit-registry) `RequiredFiles` is present, Pulsar **entirely bypasses the
command-line-scanning heuristic** and instead walks the tool directory selecting exactly the
declared files. Those files are then transferred with their relative layout preserved, landing in
the tool directory on the remote node. The net effect is **deterministic, author-controlled,
correct** staging instead of a best-effort guess — which is exactly what "systematic handling of
remotely required tool files" means.

Because `RequiredFiles` lives in `galaxy-tool-util`, the code Galaxy uses to parse the XML is the
same code Pulsar uses to resolve files against the directory — no duplicated logic and no serialized
file list to keep in sync.

## How the feature has evolved since merge

- **The parser and `RequiredFiles` class are essentially unchanged.** `find_required_files`, the four
  `type` semantics, and the default-exclude set (`tool-data`, `test-data`, `.hg`) work as they did in
  the original PR; only cosmetic formatting differs.
- **The implicit-defaults registry has grown.** `IMPLICITLY_REQUIRED_TOOL_FILES` shipped with one
  entry (`deseq2`) and now carries roughly 17 legacy Galaxy and IUC tools — for example
  [`circos`](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/circos/circos.xml)
  (ship the whole directory), the
  [`query_tabular`](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/query_tabular/query_tabular.xml)
  family (`*.py`), the `gops_*` / `fasta_*` legacy tools (`utils/*`), and
  [`shasta`](https://github.com/galaxyproject/tools-iuc/blob/a4c4c8ca75e888ea04c4a93b35b4650dcc85e5d5/tools/shasta/shasta.xml)
  (`configs/*`).
- **The `type` set is stable.** No new match types were added; globs already cover the `**`,
  `*.ext`, and `dir/*` cases the registry uses.
- **The Pulsar side is stable.** The `tool_directory_required_files` field and the `FileStager`
  branch remain as introduced, and a Pulsar integration test
  (`test_integration_explicit_tool_directory_includes`) exercises the explicit-declaration path.

No profile-version enforcement has been switched on yet: the schema still only *warns* that a future
tool profile may disable the implicit heuristic. As of 2026-07 the legacy scan is still the default when no
`<required_files>` block or registry entry applies — which is exactly why declaring the block
yourself is the reliable choice.

## Concrete XML examples

Drawn from the schema and the feature's
[unit tests](https://github.com/galaxyproject/galaxy/blob/fdf016e6f90f68924b7dc9d2d5d193a52ed923de/test/unit/tool_util/test_required_files.py):

**Single literal file** (default `type="literal"`):

```xml
<required_files>
  <include path="my_script.R" />
</required_files>
```

**Glob include with a literal exclude** — ship every `.R` except one:

```xml
<required_files>
  <include path="*.R" type="glob" />
  <exclude path="other_script.R" />
</required_files>
```

**Regex include + glob exclude:**

```xml
<required_files>
  <include path=".*R" type="regex" />
  <exclude path="other_script*" type="glob" />
</required_files>
```

**Disable the default excludes** — needed only if you genuinely must ship something under `.hg/`,
`test-data/`, or `tool-data/`:

```xml
<required_files extend_default_excludes="false">
  <include path="*.R" type="glob" />
</required_files>
```

**Prefix (subdirectory) include** — ship a whole helper directory:

```xml
<required_files>
  <include path="scripts/" type="prefix" />
</required_files>
```

**Ship the entire tool directory** (the equivalent of the registry's `REQUIRE_FULL_DIRECTORY`):

```xml
<required_files>
  <include path="**" type="glob" />
</required_files>
```

## References

Galaxy core:

- [`tool_util/parser/interface.py`](https://github.com/galaxyproject/galaxy/blob/fdf016e6f90f68924b7dc9d2d5d193a52ed923de/lib/galaxy/tool_util/parser/interface.py) — the `RequiredFiles` class, `find_required_files`, and the `parse_required_files` hook
- [`tool_util/parser/xml.py`](https://github.com/galaxyproject/galaxy/blob/fdf016e6f90f68924b7dc9d2d5d193a52ed923de/lib/galaxy/tool_util/parser/xml.py) — XML parsing of the block
- [`tool_util/xsd/galaxy.xsd`](https://github.com/galaxyproject/galaxy/blob/fdf016e6f90f68924b7dc9d2d5d193a52ed923de/lib/galaxy/tool_util/xsd/galaxy.xsd) — schema and `type` enum
- [`galaxy/tools/__init__.py`](https://github.com/galaxyproject/galaxy/blob/fdf016e6f90f68924b7dc9d2d5d193a52ed923de/lib/galaxy/tools/__init__.py) — the `IMPLICITLY_REQUIRED_TOOL_FILES` registry and resolution
- [`galaxy/jobs/runners/pulsar.py`](https://github.com/galaxyproject/galaxy/blob/fdf016e6f90f68924b7dc9d2d5d193a52ed923de/lib/galaxy/jobs/runners/pulsar.py) — passes the object into `ClientJobDescription`
- [`test/unit/tool_util/test_required_files.py`](https://github.com/galaxyproject/galaxy/blob/fdf016e6f90f68924b7dc9d2d5d193a52ed923de/test/unit/tool_util/test_required_files.py) — unit tests

Pulsar:

- [`client/staging/__init__.py`](https://github.com/galaxyproject/pulsar/blob/b3a2c228772272da73d107413445e170619c032b/pulsar/client/staging/__init__.py) — `ClientJobDescription.tool_directory_required_files`
- [`client/staging/up.py`](https://github.com/galaxyproject/pulsar/blob/b3a2c228772272da73d107413445e170619c032b/pulsar/client/staging/up.py) — the explicit-vs-legacy `FileStager` branch and the heuristic being replaced
- [`test/integration_test.py`](https://github.com/galaxyproject/pulsar/blob/b3a2c228772272da73d107413445e170619c032b/test/integration_test.py) — `test_integration_explicit_tool_directory_includes`

Documentation:

- [Galaxy tool-XML `required_files` reference](https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-required-files)
- [Pulsar documentation](https://pulsar.readthedocs.io/)
- [galaxyproject/galaxy#12250](https://github.com/galaxyproject/galaxy/pull/12250) — the PR that introduced the feature
