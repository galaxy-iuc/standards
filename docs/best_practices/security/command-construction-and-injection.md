---
orphan: true
---

# Corpus Research: Command Construction and Injection (AI Generated)

Research snapshot: `galaxyproject/tools-iuc` reviews and current Galaxy tool
semantics, **2026-07-23**.

> This is AI-generated research, not normative IUC policy. See the curated
> [Tool Security Checklist](../security) for current guidance.

## 1. The recurring data flow

Most candidate findings can be expressed as:

```text
Galaxy value
  → Cheetah object / Python expression
  → generated shell or script text
  → shell or another interpreter
```

Common sources are text parameters, dataset paths, metadata, and collection
identifiers. Common sinks are `<command>`, `bash -c`, `samtools ... -c`,
generated command files, `python -c`, `R -e`, `awk`, and application-specific
expression options.

The analyzer must model each parser boundary independently. A value may be:

- safe as one shell argument but unsafe inside the `awk` program carried by that
  argument;
- safe in JSON but unsafe after an application interprets that JSON value as a
  template;
- valid biological syntax but unsafe in a shell;
- sanitized for a shell yet unsuitable as a unique filename.

## 2. Cheetah is a privileged execution phase

Galaxy renders `<command>` and templated `<configfile>` content on the Galaxy
server during job preparation. That template code runs before the tool command,
outside the isolation supplied by the eventual job container.

The official
[user-defined tool security documentation](https://docs.galaxyproject.org/en/latest/admin/user_defined_tools.html)
demonstrates why XML/Cheetah tool definitions are privileged: template code can
reach the Galaxy process environment and filesystem. A scanner therefore needs
template-phase sinks in addition to job-command sinks:

- `#import` and `#from` of filesystem, process, or network modules;
- `open`, `Path` I/O, `os.*`, `subprocess`, and network clients;
- `$__app__` or other Galaxy internals;
- `.unsanitized` or direct raw-value access;
- template-time filesystem reads of dataset paths.

Containerization can reduce the impact of the resulting job process. It does
not sandbox Cheetah evaluation.

## 3. Single quotes are the baseline, not the whole model

The most frequent review instruction is to single-quote text, data paths, and
output paths:

```xml
<!-- Unsafe -->
tool --input $input --pattern "$pattern"

<!-- Established IUC form -->
tool --input '$input' --pattern '$pattern'
```

Double quotes still permit shell parameter expansion and command substitution.
Unquoted values also undergo word splitting and glob expansion.

Representative review threads:

- [#2117](https://github.com/galaxyproject/tools-iuc/pull/2117#discussion_r222377191)
  explicitly explains why double quotes can be a security issue.
- [#5482](https://github.com/galaxyproject/tools-iuc/pull/5482#discussion_r1329895430)
  requests single quotes for every data and text parameter.
- [#7034](https://github.com/galaxyproject/tools-iuc/pull/7034#discussion_r2135964488)
  applies the same rule to paths used by `ln -s`.

False-positive control is important. Numeric parameters and fixed tokens emitted
from a closed select may not need quoting. The corpus includes reviewers
warning that unnecessary quoting can create a false sense of security.

## 4. Cheetah sanitizer semantics

Galaxy wraps parameter values so that conversion to a string applies the
parameter's sanitizer. This behavior is implemented in
[`SafeStringWrapper`](https://github.com/galaxyproject/galaxy/blob/dev/lib/galaxy/security/object_wrapper.py).

The subtle failure is assuming all Python operations necessarily use the safe
string representation. [PR #6963](https://github.com/galaxyproject/tools-iuc/pull/6963)
changed 13 wrappers to force string conversion before operations such as
`split()`:

```xml
<!-- The method call could operate on the wrapped value without the expected
     string sanitization. -->
#set values = $text_param.split(',')

<!-- The reviewed form makes the conversion explicit. -->
#set values = str($text_param).split(',')
```

The PR discussion points to Galaxy's object wrapper and explains that ordinary
`$text_param` rendering casts to string, while use inside a Python expression
did not automatically provide the same result.

Galaxy's default sanitizer is an allowlist and character mapping, not shell
escaping. It allows several characters with shell meaning, including spaces,
wildcards, and parentheses. A custom sanitizer that allows a single quote can
also break the normal `'$value'` boundary. Sanitizer configuration and quote
context must be analyzed together.

A scanner therefore needs an approximate Cheetah/Python AST. A regular
expression looking only for quotes around `$name` will miss:

- method calls;
- values unpacked from repeats and conditionals;
- list comprehensions and joins;
- formatted strings produced by `#echo`;
- shell fragments accumulated in `#set` variables.

## 5. Validators, sanitizers, and quoting are different controls

| Control | Primary effect | Common failure |
|---|---|---|
| Validator | Rejects a value before job execution | Regex validates only a prefix; domain is too broad |
| Sanitizer | Rewrites disallowed characters during rendering | Corrupts meaningful input or is bypassed in an expression |
| Shell quoting | Preserves one literal shell argument | Does not protect a nested parser |
| Data serialization | Moves a value out of executable syntax | Downstream tool later evaluates the field |

[PR #4373](https://github.com/galaxyproject/tools-iuc/pull/4373#discussion_r818837858)
is a clear validator case: free text was narrowed to biological alphabets and
punctuation to prevent code injection.

Regular-expression inputs are especially difficult. The punctuation that gives
regex its function overlaps heavily with shell syntax. The safer options are to
remove the feature, use a config/data file, or define an exact supported
grammar—rather than adding back all printable characters to a sanitizer.

Galaxy regex validators perform a prefix match. A security boundary that must
constrain the complete value therefore needs an explicit end anchor and tests
for trailing newlines or other suffixes.

## 6. Nested interpreter boundaries

The outer command may itself ask a program to execute another command:

```xml
samtools reheader -c "awk -f '$__tool_directory__/edit.awk' '$edits' -" '$input'
```

Here the shell parses the `-c` argument and `samtools` later passes it to another
shell. User values inside the nested command would need to survive both parser
boundaries.

[PR #8206](https://github.com/galaxyproject/tools-iuc/pull/8206) is the positive
counterexample:

- the nested command contains only the tool directory and a Galaxy-generated
  config-file path;
- user values are records inside the config file;
- `awk` reads those records as data;
- tabs and newlines that could create records are rejected;
- the wrapper offers no user-script escape hatch.

This is the sort of secure design a scanner must recognize and avoid flagging
merely because `sanitize="false"` appears nearby.

## 7. Config files can be data or code

`<configfiles><inputs .../>` asks Galaxy to serialize a typed representation as
JSON and is often a strong data boundary. A templated `<configfile>` is more
general: it can produce YAML, R, Python, shell, or any other text.

Classify a generated file by how the downstream application consumes it:

- JSON/tabular value read as a string or number: data sink;
- regular expression or query evaluated by the program: expression sink;
- generated R/Python/shell program: code sink;
- credential material: secret sink, for which an ordinary Galaxy config file
  is not appropriate.

Do not suppress an injection finding merely because the value first passes
through a config file.

## 8. Expression tools

[PR #2444](https://github.com/galaxyproject/tools-iuc/pull/2444#issuecomment-509947707)
records a review of user-controlled table expressions. The key recommendation
was a whitelist-only model: explicit allowed names and operations rather than a
denylist of dangerous Python, NumPy, or pandas functionality.

For an expression feature, review:

1. allowed tokens and grammar;
2. name and attribute lookup;
3. call targets;
4. subscripting and object traversal;
5. implicit conversions and overloaded operators;
6. resource-exhaustion expressions;
7. whether the environment exposes files, imports, or process APIs.

If arbitrary code execution is the actual feature, it should not be disguised
as ordinary tool parameterization.

## 9. Candidate static checks

High-confidence:

- unquoted text/data/identifier flow into shell syntax;
- dynamic value inside `sh -c`, `bash -c`, backticks, or `$()`;
- direct construction of Python/R/awk source from a parameter;
- explicit `eval` or `exec` of a user-derived string;
- Cheetah text-object method calls that bypass the expected safe conversion.
- template-phase process, filesystem, network, application-internal, or raw
  parameter access.

Context-dependent:

- permissive sanitizer reaching a command;
- a free-text parameter without a validator;
- `sanitize="false"` where the value is later consumed only as data;
- fixed select tokens that resemble shell syntax;
- application expression options with an independently enforced grammar.

## 10. Review tests

Security regression tests should exercise the boundary rather than merely run a
default input:

- whitespace and glob characters;
- single and double quotes;
- `$()`, backticks, semicolons, pipes, redirects, and newlines;
- values that normalize to the same filename;
- punctuation that must remain valid when safely transported as data;
- an assertion that no marker command or unexpected file is executed/created.
