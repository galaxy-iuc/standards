Tool Security Checklist
=======================

Galaxy tool wrappers sit at a trust boundary. Values supplied through tool
parameters, datasets, collection identifiers, metadata, uploaded files, and
credentials may reach shells, generated scripts, filenames, deserializers,
remote services, or browser-rendered output.

The unifying principle behind every item below:

    Treat every user-controlled value as data. Track how it is transformed and
    where it is consumed. Quoting, validation, and sanitization are
    context-specific controls, not interchangeable guarantees.

The Checklist
-------------

#. :ref:`Single-quote dynamic values in shell commands <security-shell-quoting>`
   — quote text, data paths, collection values, input and output paths, and inspect nested shell contexts separately.
#. :ref:`Constrain free text to the smallest useful language <security-free-text>`
   — prefer typed parameters and selects; otherwise use validators and a deliberately narrow sanitizer.
#. :ref:`Treat identifiers and generated filenames as untrusted <security-identifiers>`
   — quote identifiers for the shell and normalize them before filesystem use without creating collisions.
#. :ref:`Preserve sanitization through Cheetah expressions <security-sanitizer-semantics>`
   — do not assume that method calls, joins, or Python expressions sanitize wrapped parameter values.
#. :ref:`Keep Cheetah templating side-effect free <security-cheetah-side-effects>`
   — template evaluation runs with Galaxy's privileges before the job or container starts.
#. :ref:`Keep user values as data, never generated code <security-data-not-code>`
   — use config files, JSON, or strict allowlists instead of ``eval``, user scripts, or interpolated program text.
#. :ref:`Treat uploaded serialized objects and archives as active input <security-unsafe-formats>`
   — pickle-like formats may execute code and archive extraction may write outside the job directory.
#. :ref:`Keep credentials out of commands, arguments, and logs <security-credentials>`
   — use Galaxy credentials and an application's native environment- or file-based interface.
#. :ref:`Verify downloads and preserve transport security <security-downloads>`
   — require TLS verification, prefer immutable sources, and check downloaded content before use.
#. :ref:`Treat browser-rendered output as active content <security-active-content>`
   — raw HTML, SVG, and JavaScript require an explicit trust and containment decision.

Details
-------

.. _security-shell-quoting:

1. Single-quote dynamic values in shell commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``<command>`` block is rendered into a script and executed by a shell.
Text parameters, dataset paths, output paths, metadata, and collection values
can contain whitespace or shell metacharacters. Place each dynamic value in
single quotes so the shell receives one literal argument:

.. code-block:: xml

    <!-- WRONG: word splitting and shell expansion are possible. -->
    my_tool --input $input --label "$label" --output $output

    <!-- RIGHT: each value is one literal shell argument. -->
    my_tool --input '$input' --label '$label' --output '$output'

**Double quotes are not equivalent to single quotes**: the shell still performs
parameter expansion, command substitution, and some backslash processing
inside double quotes. Numeric parameters and fixed ``select`` values can be
different, but the safety argument must come from their type or finite value
set, not from visual similarity to a text parameter.

Quoting must match the actual interpreter. A value placed inside
``bash -c``, an ``awk`` program, an R or Python expression, or a generated
script crosses another parsing boundary. Quoting it once for the outer shell
does not make it safe for the inner language. The safer design is usually to
write values to a Galaxy ``<configfile>`` and have the program consume them as
data.

.. _security-free-text:

2. Constrain free text to the smallest useful language
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``integer``, ``float``, ``boolean``, ``select``, ``data_column``, and other
typed parameters when they describe the real input domain. A free-text
parameter gives a user a much larger language than most command-line options
need.

When text is required:

- Add a validator that rejects values outside the tool's accepted language.
  Galaxy regex validators match from the beginning, so anchor the end as well
  when the complete value must be constrained.
- Use a sanitizer that preserves only the characters the application needs.
  Do not start from ``string.printable`` unless the downstream representation
  safely supports every allowed character.
- Give validators a useful message so rejected input can be corrected.
- Test punctuation, whitespace, quotes, newlines, empty values, and boundary
  lengths, not only the default.

For example, when a sample label must contain only letters, digits,
underscores, and hyphens:

.. code-block:: xml

    <!-- WRONG: this prefix match also accepts "sample;unexpected". -->
    <param name="sample_name" type="text">
        <validator type="regex">[A-Za-z0-9_-]+</validator>
    </param>

    <!-- RIGHT: the anchors constrain the complete value. -->
    <param name="sample_name" type="text">
        <validator type="regex"
                   message="Use only letters, digits, underscores, and hyphens.">^[A-Za-z0-9_-]+$</validator>
    </param>

This validation complements, but does not replace, quoting at a shell boundary.
If the valid values form a finite set, use a ``select`` instead of free text.

Validators and sanitizers do different work. A validator rejects an invalid
value before the job starts. A sanitizer transforms characters as the value is
rendered. Silent transformation can corrupt a regular expression, sample name,
or scientific identifier, while validation can preserve the original value
and explain why it is not accepted.

The default sanitizer is a character transformation, not shell escaping; its
allowed set includes several characters with shell meaning. A custom sanitizer
that permits a single quote also invalidates the usual ``'$value'`` shell
boundary unless that quote is handled separately.

Galaxy's schema reference documents both
`validators <https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-inputs-param-validator>`__
and
`sanitizers <https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-inputs-param-sanitizer>`__.

.. _security-identifiers:

3. Treat identifiers and generated filenames as untrusted
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``element_identifier``, dataset names, metadata values, and labels are
user-influenced strings. They are not safe merely because Galaxy supplied
them. Galaxy generally works to sanitize these values, but the best practice
is still to treat them as untrusted. IUC reviews repeatedly find identifiers
used as symlink names, temporary paths, output prefixes, or fragments of
generated command files.

Two independent controls may be required:

#. **Shell safety:** single-quote the final path whenever it enters a shell
   command.
#. **Filesystem safety:** map the identifier to a deliberately small filename
   alphabet before creating a file, directory, or link.

.. code-block:: xml

    <!-- WRONG: the raw identifier controls a filename and is unquoted. -->
    ln -s '$input' $input.element_identifier

    <!-- RIGHT when the external tool does not need the original identifier. -->
    ln -s '$input' input.fasta

    <!-- RIGHT when the external tool requires a meaningful filename. -->
    #import re
    #set identifier = str($input.element_identifier)
    #set safe_identifier = re.sub(r'[^\w.-]', '_', identifier)
    ln -s '$input' '${safe_identifier}.fasta'

If the external program does not need the original identifier, prefer a fixed
filename. If it does, preserve the original value separately in data or
metadata. A replacement such as ``re.sub('[^\\w.-]', '_', value)`` can cause
different identifiers to collapse to the same filename; add a stable unique
suffix or fail on collisions when multiple collection elements are handled
together.

.. _security-sanitizer-semantics:

4. Preserve sanitization through Cheetah expressions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Galaxy wraps parameter values so their string representation is sanitized
when Cheetah renders them. That protection is not a license to perform
arbitrary Python operations on wrapped values.

Be especially careful with:

- ``.split()``, ``.strip()``, and other method calls inside ``#set`` or
  ``#echo`` expressions;
- joining lists derived from text parameters;
- formatting strings that combine parameters into shell fragments;
- directly accessing an unsanitized or internal representation;
- disabling sanitization and assuming surrounding quotes compensate.

When transforming a text parameter in Cheetah, explicitly convert the
parameter to ``str`` *before* calling methods such as ``split`` or ``strip``,
then quote each resulting shell argument. In
2025, a single IUC change had to add explicit ``str(...)`` conversions across
13 wrappers because Python-expression use bypassed the expected sanitizer.

Do not reduce this rule to "add ``str`` everywhere": the desired result is
that the value is sanitized exactly once for the context where it is consumed.
Values written to JSON or another data-only config may legitimately preserve
characters that would be unsafe in a shell fragment.

.. _security-cheetah-side-effects:

5. Keep Cheetah templating side-effect free
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Galaxy evaluates Cheetah in ``<command>`` and templated ``<configfile>`` blocks
on the Galaxy server while preparing the job. This happens before the command
runs and therefore before a job container or remote execution environment can
isolate it.

Do not use template expressions to:

- open, write, list, or stat server files;
- import and call ``os``, ``pathlib``, ``subprocess``, or network clients;
- query internal application objects such as ``$__app__``;
- access an unsanitized internal parameter representation;
- perform work that belongs in the job command or a declared helper script.

Use Galaxy dataset metadata rather than opening an input path during template
evaluation. Put runtime work in a tool dependency or a reviewed helper that
runs as part of the job.

This is both a security and remote-execution rule. Standard tool templates have
access to Galaxy's process environment and filesystem; a container around the
eventual command does not contain template-phase behavior. Galaxy's
`user-defined tool security documentation
<https://docs.galaxyproject.org/en/latest/admin/user_defined_tools.html>`__
describes why untrusted XML/Cheetah tools cannot be treated as ordinary
user-authored jobs.

.. _security-data-not-code:

6. Keep user values as data, never generated code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Avoid inserting user-controlled values into Python, R, JavaScript, ``awk``,
regular-expression replacement programs, or arbitrary shell snippets.
Quoting rules are different for every language and become difficult to reason
about when interpreters are nested.

Prefer:

- a Galaxy ``<configfiles><inputs .../>`` typed JSON document, or a templated
  ``<configfile>`` only when the target format is consumed strictly as data;
- a tabular key/value file parsed by the wrapped application;
- fixed commands selected with a ``select`` parameter;
- a narrow, explicit allowlist when expression support is the purpose of the
  tool.

Do not expose ``eval``, ``exec``, user-provided script bodies, arbitrary
command options, or "run your own command" escape hatches in a general-purpose
wrapper. If controlled expression evaluation is unavoidable, define allowlists for names,
operators, attributes, and call targets, then test bypasses such as attribute
traversal and unexpected object types.

Galaxy documents generated
`config files and JSON input files <https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-configfiles>`__,
which keep values out of command syntax and make the data boundary reviewable.
A templated config file can also generate Python, R, shell, or another
executable language; scan it according to that target grammar rather than
assuming every config file is safe.

.. _security-unsafe-formats:

7. Treat uploaded serialized objects and archives as active input
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some formats are executable representations rather than passive data.
Python pickle, RData/RDS objects, and some machine-learning checkpoint formats
can construct objects or invoke code while loading. A datatype extension does
not make an uploaded object trustworthy.

Before accepting such an input:

- determine whether the library has a restricted or data-only loading mode;
- prefer an interchange format that cannot encode executable objects;
- limit loading to tool-produced outputs when provenance can be enforced;
- document that public, multi-user Galaxy deployments have a different threat
  model from private trusted-user installations;
- treat a container as damage containment, not proof that deserialization is
  safe.

Archive extraction is a related boundary. Validate each member's resolved
destination before extraction, reject absolute paths and ``..`` traversal, and
consider links and special files. Extract only the members the tool actually
needs.

.. _security-credentials:

8. Keep credentials out of commands, arguments, and logs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Passwords, API keys, access tokens, and private endpoints must not appear in:

- literal tool XML or test fixtures;
- generated command text or Galaxy job metadata;
- command-line arguments visible in the process list;
- ``echo`` statements, standard output, standard error, or debug logs;
- output datasets or test assertions.

Galaxy 25.1 introduced ``<credentials>`` requirements that inject variables
and secrets into the job environment without making them Cheetah variables.
Use an application's native environment-variable lookup when it does not copy
the value onto the command line. If the application accepts a credential file,
use a runtime helper that reads the environment and creates a private file with
restrictive permissions, then pass only the file path. Do not use an ordinary
templated ``<configfile>`` for a secret: credentials are intentionally not
Cheetah variables, and ordinary generated config files are not secret storage.

Do not expand a secret-bearing environment variable as a command-line
argument. Besides process-list exposure, Galaxy's credential values are not
sanitized for shell use. Document the remaining exposure: job scripts may be
visible to Galaxy administrators, depending on deployment retention and
access policy.

See the Galaxy schema's
`credential security considerations
<https://docs.galaxyproject.org/en/latest/dev/schema.html#tool-requirements-credentials>`__.

.. _security-downloads:

9. Verify downloads and preserve transport security
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Data Managers and tools that fetch remote content extend the trust boundary to
another service.

- Use HTTPS and do not disable hostname or certificate verification.
- Prefer versioned, immutable URLs over branch heads or "latest" endpoints.
- Verify a checksum obtained through an independent, trusted channel.
- Fail the job on verification errors; do not continue with partial content.
- Avoid executing a downloaded script or unpacking an archive before
  verification.
- Record the source URL and version in the resulting data-table entry or
  provenance where possible.
- Do not pass an unconstrained user URL directly to ``curl``, ``wget``, or a
  language HTTP client. Restrict schemes and hosts, reject local/private
  destinations and embedded credentials, re-check redirects, and limit size
  and time. Direct wrapper downloads bypass Galaxy's own URL-fetch allowlist
  and private-network protections.

A checksum detects corruption or substitution relative to the expected
artifact; it does not establish that the upstream artifact itself is benign.
Dependency versions and containers should also remain pinned according to the
tool dependency best practices.

.. _security-active-content:

10. Treat browser-rendered output as active content
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HTML, SVG, and JavaScript can execute in a browser or load remote resources.
Do not publish raw active content merely because it is convenient for
presenting a report.

Prefer Galaxy-native datasets and collections, static images, or a narrowly
defined format that Galaxy can render through an established safe path. When
active content is essential, identify which values are user controlled,
escape them for the correct HTML/attribute/URL/JavaScript context, apply the
Galaxy rendering and isolation mechanisms intended for that datatype, and
document the trust decision.

Galaxy's safe defaults sanitize HTML unless an administrator allowlists the
tool, and serve SVG/XML-like XSS-prone content as plain text unless an
administrator enables active serving. Emitting active content therefore creates
an administrator trust decision; a wrapper must not assume every deployment
keeps the same rendering policy.

See Galaxy's
`HTML sanitization option
<https://docs.galaxyproject.org/en/latest/admin/galaxy_options.html#sanitize-all-html>`__
and
`XSS-vulnerable MIME-type option
<https://docs.galaxyproject.org/en/latest/admin/galaxy_options.html#serve-xss-vulnerable-mimetypes>`__.
