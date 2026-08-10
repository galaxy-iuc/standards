Licensing and Use Restrictions
==============================

The IUC accepts wrappers for software under an OSI-approved license. That rule
answers the common case, but it does not answer every case, because the
restricted artifact is frequently not the tool's own code: it is an optional
dependency, a reference dataset, a model, or a term that binds the organization
hosting the server rather than the person submitting the job.

This page is about those situations, and about the small number of wrappers
whose underlying software carries use restrictions of its own.

.. warning::

    Nothing on this page is legal advice. The goal is narrower: make restrictions
    **visible**, record upstream permission, and tell administrators their
    obligations before they install the tool.

The Checklist
-------------

#. :ref:`Start from the OSI rule <licensing-osi>`:
   most restricted cases the IUC actually encounters involve data, models, or
   dependencies rather than the wrapped tool's own license.
#. :ref:`Separate the four licensing layers <licensing-four-licenses>`:
   the wrapper, the wrapped software, its dependencies, and any reference data
   or models it uses.
#. :ref:`Confirm redistribution is permitted before writing the wrapper <licensing-redistribution>`:
   normally use a Bioconda package and container; otherwise document an
   administrator-managed installation path.
#. :ref:`Read the actual terms, not the SPDX identifier <licensing-read-terms>`:
   some licenses constrain the person submitting the job, some constrain the
   organization hosting the server. Only the first can be handled in a wrapper.
#. :ref:`State the restriction in help and metadata <licensing-declare>`:
   an administrator deciding whether to install a tool should not have to read
   the ``<command>`` block to discover it is encumbered.
#. :ref:`Gate the smallest thing that is actually restricted <licensing-scope-the-gate>`:
   a restricted model, database, or optional analysis should not block the
   unrestricted parts of a tool.
#. :ref:`Use the current affirmation pattern, and know what it does not do <licensing-current-pattern>`:
   it stores ordinary parameter state rather than a first-class acceptance
   record, and workflow runs need not prompt the executing user.

Details
-------

.. _licensing-osi:

1. Start from the OSI rule
~~~~~~~~~~~~~~~~~~~~~~~~~~

`CONTRIBUTING.md <https://github.com/galaxyproject/tools-iuc/blob/main/CONTRIBUTING.md>`__
states that "the tool must be licensed to allow use by anyone" and points at the
`OSI list <https://opensource.org/licenses>`__; the pull request template asks
the contributor to confirm that the "[l]icense permits unrestricted use
(educational + commercial)". The policy was adopted in
`tools-iuc#2102 <https://github.com/galaxyproject/tools-iuc/pull/2102>`__ in
October 2018, following
`tools-iuc#2054 <https://github.com/galaxyproject/tools-iuc/issues/2054>`__,
which was prompted by the MEME Suite: already wrapped here, distributed through
Bioconda, and not open source.

So the first question about a restricted tool is whether it belongs in this
repository at all. Frequently it does not, and no amount of wrapper engineering
changes that.

Two complications remain despite the rule:

**The encumbered artifact is often not the tool's code.** Clair3, InterProScan,
Funannotate, GEMINI, and EGSEA all carry OSI-approved licenses and are each
restricted elsewhere: a basecalling model, separately licensed member analyses,
a third-party gene predictor, CADD scores, KEGG and MSigDB gene sets. Such
wrappers satisfy the rule and still need everything on this page.

**A few wrappers predate the rule.** The MEME Suite wrappers, ``meme_chip``,
``pear``, and ``maker`` were added before October 2018 and are maintained under
their original terms. ``sfold``, added in 2024, is the only later addition for
software without an OSI-approved license. Treat it as an exception rather than a
precedent.

Tool repositories that do not apply this rule may still find the sections below
useful, though section 3 assumes the Bioconda route the IUC relies on.

.. _licensing-four-licenses:

2. Separate the four licensing layers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Do not conflate these independent layers:

**The wrapper.** The ``license`` attribute on ``<tool>`` is an SPDX identifier
or URI for *the tool XML and associated scripts you wrote*. Per the
`Galaxy tool XML schema <https://docs.galaxyproject.org/en/latest/dev/schema.html#tool>`__,
it "covers the tool XML and associated scripts shipped with the tool". It says
nothing about the wrapped software.

**The wrapped software.** Galaxy currently has **no** tool XML element for its
license, a long-standing gap tracked in
`galaxyproject/galaxy#12663 <https://github.com/galaxyproject/galaxy/issues/12663>`__
and `galaxyproject/galaxy#8006 <https://github.com/galaxyproject/galaxy/issues/8006>`__.

**Its dependencies.** A permissively licensed program can pull in an encumbered
one. For example, several InterProScan analyses are separately licensed, absent
from its conda package, and must be installed by the administrator.

**Reference data and models.** The restricted artifact may not be code. Clair3
is BSD-3-Clause, but its Rerio models use the Oxford Nanopore Technologies
Public License; GEMINI is MIT, but CADD scores are non-commercial only.

.. _licensing-redistribution:

3. Confirm redistribution is permitted before writing the wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most IUC tools obtain their dependencies through a Bioconda package and,
downstream of that, a public BioContainers or mulled image. Bioconda's
contributor checklist requires that the "`[l]icense allows redistribution and
license is indicated in meta.yaml
<https://bioconda.github.io/contributor/guidelines.html>`__". Before writing the
wrapper, confirm that the terms permit both forms of distribution. For
academic-use software, ask explicitly rather than inferring permission from the
availability of an upstream download.

Three outcomes, all of which occur in practice:

**The license permits redistribution with restrictions on use.** This is the
case the rest of this page addresses. Record the terms and ship the license text
in the recipe. For example, ``license: Custom`` and ``license_file: COPYING`` for
`meme <https://github.com/bioconda/bioconda-recipes/tree/master/recipes/meme>`__,
and the SPDX identifier ``CC-BY-NC-SA-3.0`` for
`pear <https://github.com/bioconda/bioconda-recipes/tree/master/recipes/pear>`__.
Values such as ``OTHER`` or ``Custom`` do not themselves grant redistribution;
read the referenced terms.

**The license is silent or ambiguous, and upstream grants permission.** Ask
upstream in writing and link the answer from the wrapper. MAKER is the model:
its recipe says ``GPL-3.0-or-later``, its terms limit use, and its author
`explicitly permitted Bioconda and Galaxy distribution
<https://github.com/galaxyproject/iwc/pull/47#issuecomment-962260646>`__.
``maker.xml`` links that grant beside the affirmation parameter. Do not treat
silence as permission.

**Redistribution is not permitted.** Then Bioconda cannot ship the software and
standard automatic installation is unavailable. Two administrator-managed
patterns have been used:

- **A placeholder package plus a registration script.** Historically,
  Bioconda's ``gatk`` recipe installed a stub and a ``gatk-register`` command
  for an administrator-supplied archive. The current recipe no longer uses this
  arrangement.
- **An optional path in the wrapper that assumes a manual installation.**
  ``interproscan.xml`` places its licensed analyses behind a ``<conditional>``
  that documents the requirement and tests their default deactivated state.

.. _licensing-read-terms:

4. Read the actual terms, not the SPDX identifier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"Non-commercial" is not one restriction. Determine who the terms bind.

**Restrictions on the submitting user's purpose** can be addressed with an
affirmation. For example, MEME permits educational, research, and non-profit use
without fee but directs commercial users to its licensing office.

**Restrictions on the hosting organization.** These bind the deployment, and no
user-facing checkbox can satisfy them. Examples include terms that limit the
eligible institutions, installation sites, users, or hosted services. State
these restrictions in ``<help>`` and require the administrator to establish
that the deployment is permitted.

The general signal: **if you find yourself writing an affirmation whose text the
submitting user is not actually in a position to assert, the restriction is not
one a wrapper can handle.** Escalate it to the administrator.

.. _licensing-declare:

5. State the restriction in help and metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make restrictions visible without requiring anyone to inspect ``<command>``:

- **Lead with the restriction in** ``<help>``. Name the license, the affected
  party, the canonical terms, and any commercial-licensing contact.
- **Treat a citation requirement as a license condition, not a courtesy.** List
  required publications in ``<citations>`` and state the obligation in
  ``<help>``. This supports compliance but does not satisfy the user's citation
  obligation on their behalf.
- **Repeat it in the affirmation label.** Name the terms being affirmed rather
  than asking only for a generic non-commercial certification.
- **Do not overload the** ``license`` **attribute on** ``<tool>``. It describes
  the wrapper, not its underlying software, and Galaxy does not enforce it.
- **Cross-reference bio.tools** with ``<xrefs>`` as normal and keep its
  `machine-readable license field
  <https://biotools.readthedocs.io/en/latest/api_usage_guide.html#license>`__
  current. A single controlled value cannot express every custom use or
  deployment restriction, so it complements rather than replaces the wrapper's
  help and gate.

.. _licensing-scope-the-gate:

6. Gate the smallest thing that is actually restricted
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the tool is encumbered, gate the tool. If only one input, model, database, or
optional analysis is encumbered, gate only that path. Over-blocking an
unrestricted analysis encourages reflexive acceptance. ``egsea.xml`` shows the
cost: the software is GPL-3 and the restriction belongs to its optional KEGG and
MSigDB gene sets, but the certification sits at the top level of ``<inputs>``,
so every run is gated whether or not those sets are selected.

``clair3.xml`` is the pattern to copy for the conditional case. The restriction
applies only when the selected model comes from the Rerio data table, so the
guard tests both the affirmation and the provenance of the selection:

.. code-block:: cheetah

    #if $model_source.source == "datatable"
        #set model_path = $model_source.model.fields.path
        #if $model_source.model.fields.source == "rerio" and $ont_license_agree != "true"
            echo "You must agree to the terms of the Oxford Nanopore Technologies, Ltd. Public License agreement to use Rerio models." >&2 &&
            exit 2 ;
        #end if
    #end if

Note that this cannot be expressed with a ``<validator>``, because the condition
depends on another parameter's selected data-table row; it has to be a Cheetah
guard. Its test suite also verifies the expected failure and error message.

Where the restricted component is simply absent from the installation, as in the
InterProScan case, a conditional that documents the manual-installation
requirement is preferable to a certification, since there is nothing for the
user to certify.

.. _licensing-current-pattern:

7. Use the current affirmation pattern, and know what it does not do
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Until Galaxy offers a first-class mechanism, use an unchecked boolean with an
expression validator:

.. code-block:: xml

    <param name="non_commercial_use" type="boolean" checked="False"
           label="I certify that I am not using this tool for commercial purposes.">
      <validator type="expression" message="This tool is only available for non-commercial use.">value == True</validator>
    </param>

Back it with a guard in ``<command>``:

.. code-block:: xml

    <token name="@CHECK_NON_COMMERCIAL_USE@"><![CDATA[
        #if not $non_commercial_use
            >&2 echo "this tool is only available for non commercial use";
            exit 1;
        #end if
    ]]></token>

Use ``non_commercial_use`` for a purpose certification, or a name derived from
the specific terms being affirmed. Put the affirmation last in ``<inputs>``,
share it through a macro within one Tool Shed repository, set it in every test,
and add a test for the refusal path. ``planemo lint`` does not enforce this
convention.

This workaround has three important limitations:

1. **The executing user may never see it.** A workflow normally stores the
   boolean in the step, so its run form does not prompt the user again.
2. **Ordinary parameter state stands in for acceptance.** Galaxy retains the
   checkbox value in job and workflow state, indirectly associating it with a
   user and time. It is not, however, a first-class, versioned acceptance event
   that can be reviewed or revoked independently. Reruns may reuse the value
   without prompting the user again.
3. **It is modeled as a tool input.** The value appears in job parameters, tool
   state, API responses, rerun forms, and every workflow that embeds the tool.
   Because the mechanism is a convention rather than a declaration, wrappers
   can also apply it inconsistently.
