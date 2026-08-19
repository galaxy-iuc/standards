---
orphan: true
---

# Corpus Research: Identifiers, Filenames, and Sanitization (AI Generated)

Research snapshot: `galaxyproject/tools-iuc` reviews, **2026-07-23**.

> This is AI-generated research, not normative IUC policy. See the curated
> [Tool Security Checklist](../security) for current guidance.

## 1. Why identifiers are a recurring source

The candidate corpus contains 157 comments across 88 PRs mentioning
`element_identifier` or an element identifier. IUC wrappers often use an
identifier to give a collection element a useful external-tool filename:

```text
element_identifier
  → generated path or symlink name
  → command-line argument or application-generated command file
```

Identifiers can contain spaces, quotes, slashes, shell metacharacters, Unicode,
and repeated names. They are user-influenced metadata, not trusted constants.

## 2. Shell safety and filename safety are separate

Quoting prevents a shell from interpreting a completed path:

```xml
ln -s '$dataset' '$safe_name'
```

It does not decide whether `$safe_name`:

- contains `/`, `..`, an absolute-path prefix, or a platform separator;
- begins with `-` and is interpreted as an option by a later tool;
- collides with another normalized identifier;
- exceeds filesystem or application limits;
- has an extension that changes application behavior.

Conversely, replacing punctuation in a filename does not remove the need to
quote the result when it enters a shell.

## 3. Representative fixes

[PR #3981](https://github.com/galaxyproject/tools-iuc/pull/3981) fixed Roary
when collection identifiers were copied into filenames that were later written
unquoted into commands. The wrapper changed from the raw identifier to:

```python
re.sub(r"[^\w-]", "_", str(element_identifier))
```

and single-quoted the resulting filename.

Other recurring review forms include:

- "sanitize the symlink name";
- "clean the element identifier for characters harmful on the command line";
- "hardcode the filename if the application does not preserve or expose the
  original identifier";
- "use `element_identifier` rather than Galaxy's internal dataset filename,
  then normalize it."

## 4. Collision and identity hazards

Lossy normalization is not injective:

```text
sample/a  → sample_a
sample:a  → sample_a
sample a  → sample_a
```

When multiple collection elements are materialized together, the later file may
overwrite the earlier one or the tool may associate output with the wrong
sample.

Safer strategies:

- use a fixed sequential or generated filename and maintain a separate mapping
  table;
- append a stable digest or collection index;
- detect duplicate normalized values and fail with a useful error;
- preserve the original identifier only in a data/config field that supports
  it safely;
- use a temporary subdirectory created by Galaxy and keep every path beneath it.

The scanner should downgrade a finding when a wrapper uses a fixed/generated
filename plus a data-only mapping instead of placing the original identifier in
the filesystem.

## 5. Path containment

Normalization should enforce a path policy:

1. reject absolute paths;
2. reject or remove path separators;
3. reject `.` and `..` path components;
4. join beneath a known working-directory root;
5. resolve and verify containment if links or pre-existing paths are possible;
6. pass `--` before a user-derived positional filename when the application
   supports it.

For archives, containment must be applied to every archive member and link
target, not only the archive's top-level directory.

## 6. Sanitizer design

Galaxy's default text sanitizer allows a documented set of common punctuation
and maps invalid characters. A custom sanitizer replaces that behavior; it
does not add an independent validation layer.

Prefer allowlists shaped by the destination:

- sample code: ASCII letters, digits, `_`, `-`;
- decimal/scientific input: digits, decimal separator, sign, `e`/`E`;
- biological sequence: the relevant alphabet only;
- filename prefix: a small portable alphabet plus an explicit length limit.

Do not use `string.printable` merely to prevent Galaxy from changing a value.
If every character must be preserved, move the value to a data-only config
representation and ensure the downstream reader does not evaluate it.

## 7. Candidate static checks

High confidence:

- raw `element_identifier` in a shell command or generated shell script;
- identifier used as a path component without any normalization;
- identifier-controlled absolute path or `..` traversal;
- identifier included in a symlink target/name that escapes the working tree.

Medium confidence:

- lossy normalization without collision handling in a collection loop;
- normalized path lacking shell quoting;
- value beginning with `-` passed as a positional argument without `--`;
- extension derived from an identifier rather than a closed datatype mapping.

Useful suppressions:

- fixed filename;
- sequential generated filename with a separate mapping;
- closed allowlist validator plus quoting;
- normalization with collision detection and path containment.

## 8. Tests

Use at least two collection elements whose identifiers:

- contain spaces and punctuation;
- normalize to the same base string;
- begin with `-`;
- contain path separators or `..`;
- differ only by case if the deployment may use a case-insensitive filesystem.

Assert the external tool receives the intended distinct inputs and that every
created file remains inside the job working directory.
