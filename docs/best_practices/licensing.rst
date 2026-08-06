Licensing and Use Restrictions
==============================

Most tools wrapped by the IUC are under permissive or copyleft open source
licenses and need no special handling. A minority are not: they are free only
for academic, non-profit, or otherwise non-commercial use, they restrict
redistribution, or they restrict who may be served by an installed copy.

Wrapping such a tool is not forbidden, but it is a decision with consequences
for every administrator who installs the wrapper and every user who runs it.
This page collects what the IUC has learned doing it, and what to do while
Galaxy lacks a first-class mechanism for it.

.. warning::

    Nothing on this page is legal advice, and no contributor or reviewer should
    be expected to give any. The goal is narrower and achievable: make the
    restriction **visible**, make the upstream permission **recorded**, and make
    the obligations that fall on the administrator **legible** to that
    administrator before they install the tool.

The Checklist
-------------

#. :ref:`Separate the four licenses in play <licensing-four-licenses>`
   — the wrapper, the wrapped software, its dependencies, and any reference data or models it uses.
#. :ref:`Confirm redistribution is permitted before writing the wrapper <licensing-redistribution>`
   — no conda package, no tool; get and record explicit upstream permission where the license is silent or hostile.
#. :ref:`Read the actual terms, not the SPDX identifier <licensing-read-terms>`
   — some licenses constrain the person submitting the job; some constrain the organization hosting the server. Only the first can be handled in a wrapper.
#. :ref:`State the restriction in help and metadata <licensing-declare>`
   — an administrator deciding whether to install a tool should not have to read the ``<command>`` block to discover it is encumbered.
#. :ref:`Gate the smallest thing that is actually restricted <licensing-scope-the-gate>`
   — a restricted model, database, or optional analysis should not block the unrestricted parts of a tool.
#. :ref:`Use the current affirmation pattern, and know what it does not do <licensing-current-pattern>`
   — a boolean plus a validator, plus a Cheetah guard, is all that is available today; it records no acceptance, is not audited, and is not shown when the tool runs inside a workflow.

Details
-------

.. _licensing-four-licenses:

1. Separate the four licenses in play
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These are routinely conflated, and conflating them is how encumbered tools end
up looking unencumbered:

**The wrapper.** The ``license`` attribute on ``<tool>`` is an SPDX identifier
or URI for *the tool XML and associated scripts you wrote*. Per the
`Galaxy tool XML schema <https://docs.galaxyproject.org/en/latest/dev/schema.html#tool>`__,
it "covers the tool XML and associated scripts shipped with the tool". Most IUC
wrappers declaring it use ``license="MIT"``. It says nothing about the wrapped
software.

**The wrapped software.** MEME, Sfold, MAKER, PEAR. This is the license that
matters for the questions on this page, and Galaxy currently has **no** tool XML
element that expresses it — a long-standing gap tracked in
`galaxyproject/galaxy#12663 <https://github.com/galaxyproject/galaxy/issues/12663>`__
and `galaxyproject/galaxy#8006 <https://github.com/galaxyproject/galaxy/issues/8006>`__.

**Its dependencies.** A permissively licensed program can pull in an encumbered
one. InterProScan is a good example: the InterProScan distribution is open
source, but several member analyses it can dispatch to (Phobius, SignalP, TMHMM,
and SMART's licensed components) are separately licensed, are not shipped in the
conda package, and must be installed by the administrator.

**Reference data and models.** Increasingly the encumbered artifact is not code
at all. Clair3 is BSD-3-Clause, but the Rerio basecalling models it can use are
under the Oxford Nanopore Technologies Public License. GEMINI is MIT, but CADD
scores are non-commercial only. A tool whose code license is clean may still
need a gate on a data path.

.. _licensing-redistribution:

2. Confirm redistribution is permitted before writing the wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An IUC tool needs an installable dependency, in practice a Bioconda package —
and, downstream of that, a public BioContainers or mulled image. Bioconda's
contributor checklist requires that the "`[l]icense allows redistribution and
license is indicated in meta.yaml
<https://bioconda.github.io/contributor/guidelines.html>`__". So the first
question is not "may users run this?" but "may Bioconda ship it at all?" — and
then, separately, may that binary be baked into a container image published to a
public registry? The second question is not answered by the first, and for
academic-use software it is worth asking explicitly.

Three outcomes, all of which occur in practice:

**The license permits redistribution with restrictions on use.** This is the
common case for academic-use software, and it is the one the rest of this page
is about. The recipe declares the terms and ships the license text — for example
``license: Custom`` with ``license_file: COPYING`` for
`meme <https://github.com/bioconda/bioconda-recipes/tree/master/recipes/meme>`__,
and the SPDX identifier ``CC-BY-NC-SA-3.0`` for
`pear <https://github.com/bioconda/bioconda-recipes/tree/master/recipes/pear>`__.

Note that a recipe recording terms is not the same as a recipe asserting a
redistribution grant. ``license: OTHER`` or ``Custom`` means only that no SPDX
identifier fits; someone still has to read the file that ``license_file`` points
at. That file is useful beyond compliance: the canonical terms already exist as
text in a known place, so a wrapper that needs to display them does not have to
transcribe them.

**The license is silent or ambiguous, and upstream grants permission.** Ask
upstream, in writing, and record the answer somewhere durable. MAKER is the
model here. The Bioconda recipe declares ``GPL-3.0-or-later``, but MAKER's
actual terms are academic-use; Mark Yandell was asked directly and replied
(quoted in
`galaxyproject/iwc#47 <https://github.com/galaxyproject/iwc/pull/47#issuecomment-962260646>`__):

    We give permission for Bioconda and Galaxy Project to distribute MAKER2/3
    through their tool/package management system. MAKER2/3 is free for academic
    use, but commercial Bioconda and Galaxy users of MAKER2/3 still need a
    license […]. Bioconda and Galaxy project are not responsible for users who
    have not properly licensed MAKER.

``maker.xml`` carries a comment pointing at that permission, immediately above
the parameter that implements it. Do the same: a link to the grant in the
wrapper is worth more than the grant existing in someone's inbox.

.. code-block:: xml

    <!-- More info on licensing in https://github.com/galaxyproject/iwc/pull/47#issuecomment-962260646 -->

If upstream does not reply, you do not have permission. Silence is not a grant,
and a wrapper is not the place to resolve the ambiguity.

**Redistribution is not permitted.** Then the software cannot be packaged, and
neither Bioconda nor the IUC can make it installable. There is no
``signalp``, ``tmhmm``, ``phobius``, or ``rnammer`` recipe in Bioconda for
exactly this reason. Two established escapes exist, and both push the work onto
the administrator:

- **A placeholder package plus a registration script.** Bioconda's ``gatk``
  recipe installs a stub that prints "Due to license restrictions, this recipe
  cannot distribute and install GATK directly" and a ``gatk-register`` command
  that copies in an administrator-supplied archive.
- **An optional path in the wrapper that assumes a manual installation.**
  ``interproscan.xml`` exposes its licensed member analyses behind a
  ``<conditional>`` whose help says plainly that "[t]he corresponding tools must be
  installed manually by the administrator of this Galaxy instance". The tool
  test for that path asserts the analyses report as deactivated, which is the
  honest expectation on a default installation.

.. _licensing-read-terms:

3. Read the actual terms, not the SPDX identifier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"Non-commercial" is not one restriction. Sort the terms into two piles, because
only one of them is something a tool wrapper can address.

**Restrictions on the submitting user's purpose.** MEME grants "permission to
use, copy, modify, and distribute any part of this software for educational,
research and non-profit purposes, without fee"; commercial users contact UCSD's
Office of Innovation and Commercialization. PEAR is CC-BY-NC-SA-3.0. MAKER is
free for academic use. In each case the server may host the software, and the
open question is what *this particular person* is doing with *this particular
job*. That is a question the person running the job can answer, and it is what
the affirmation checkbox is for.

**Restrictions on the hosting organization.** These bind the deployment, and no
user-facing checkbox can satisfy them. Sfold is the clearest example in the IUC
repository. Its
`academic license <https://github.com/Ding-RNA-Lab/Sfold/blob/main/license/SFOLD-ACADEMIC-LICENSE.txt>`__
states that the licensee is "a not-for-profit college or university", and that
the grant

    is limited to use on no more than five (5) computers located at the Site by
    no more than five (5) concurrent users, all of whom shall be employees of
    You […]. It does not authorize Software use by third parties at the Site or
    by anyone not located at the Site via the Internet or any other means.

and separately that the licensee may not

    perform services for any third parties using the Software, including,
    without limitation, on a service bureau basis or with an online hosted
    service.

Every obligation in that passage falls on the licensed institution, not on the
person submitting a job. A user certifying "I am not using this tool for
commercial purposes" has said nothing about seat counts, sites, or hosted
services, because they are not the party those terms bind. Whether a given
deployment sits inside such terms is a question for that deployment's
administrator, and the useful thing a wrapper can do is make sure the question
gets asked: say so plainly in ``<help>``, and seek and record explicit upstream
permission as in the MAKER case.

The general signal: **if you find yourself writing an affirmation whose text the
submitting user is not actually in a position to assert, the restriction is not
one a wrapper can handle.** Escalate it to the administrators who will install
the tool rather than dressing it up as a checkbox.

.. _licensing-declare:

4. State the restriction in help and metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Assume an administrator is deciding whether to install your tool, and a user is
deciding whether they may run it. Neither will read the ``<command>`` block.

- **Put the restriction near the top of** ``<help>``, not in a closing footnote.
  ``meme_chip.xml`` leads with a ``.. class:: warningmark`` block, and
  ``gemini_load.xml`` and ``clair3.xml`` both raise licensing in their opening
  paragraphs. ``pear.xml`` and ``sfold.xml`` put theirs in the last lines before
  ``</help>``, where a user scanning the tool form will not see it. Name the
  license, say who is restricted, and link to the canonical terms and to the
  commercial-licensing contact where one exists.
- **Treat a citation requirement as a license condition, not a courtesy.** Some
  academic grants are made in explicit consideration of it — Sfold's clause 2.8
  begins "In partial consideration of the royalty-free license rights granted
  hereunder, Licensee shall cite the following publications". Where that is the
  case, ``<citations>`` is part of compliance and its absence is a defect.
- **Repeat it in the affirmation label**, not just in help. "I certify that I am
  not using this tool for commercial purposes" is weaker than a label that names
  the license the user is accepting; ``maker.xml``'s help text on its checkbox,
  which names the licensing page and the fact that a commercial license can be
  purchased, is closer to right.
- **Do not overload the** ``license`` **attribute on** ``<tool>``. It describes
  your wrapper. Setting it to the upstream tool's license misreports the
  wrapper's own terms and still does not produce anything Galaxy acts on. SPDX
  also has no identifier for most of these agreements — Bioconda falls back to
  ``Custom`` for MEME and ``OTHER`` for Sfold for the same reason.
- **Cross-reference bio.tools** with ``<xrefs>`` as normal. It is not a license
  declaration, but it is where a licensing annotation is most likely to become
  machine-readable first.

.. _licensing-scope-the-gate:

5. Gate the smallest thing that is actually restricted
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the tool is encumbered, gate the tool. If only one input, model, database, or
optional analysis is encumbered, gate only that path. Over-blocking an
unrestricted analysis is a real cost, and it teaches users to click through
affirmations reflexively.

``egsea.xml`` shows the cost of getting this wrong. EGSEA itself is a
Bioconductor package under GPL-3; what is restricted is the KEGG and MSigDB data
that its GAGE and Pathview components can consult, as the tool's own help
explains. The wrapper nonetheless gates *every* run on an unconditional
non-commercial certification, including analyses that touch neither data source.

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
guard. Note also the accompanying test, which asserts the failure rather than
assuming it:

.. code-block:: xml

    <test expect_failure="true" expect_exit_code="2">
        ...
        <param name="ont_license_agree" value="false" />
        <assert_stderr>
            <has_line line="You must agree to the terms of the Oxford Nanopore Technologies, Ltd. Public License agreement to use Rerio models." />
        </assert_stderr>
    </test>

Where the restricted component is simply absent from the installation — the
InterProScan case — a conditional that documents the manual-installation
requirement is preferable to a certification, since there is nothing for the
user to certify.

``artic_minion.xml`` carries a hand-copied duplicate of the whole Clair3
arrangement — the same parameter name, the same guard, the same message. If you
find yourself copying this pattern into a second wrapper, put it in a shared
macro instead.

.. _licensing-current-pattern:

6. Use the current affirmation pattern, and know what it does not do
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Nine wrappers in the IUC repository currently gate every run on an ordinary
boolean: ``sfold``, five wrappers under ``tools/meme`` (``dreme``, ``fimo``,
``meme``, ``meme_psp_gen``, ``streme``), ``meme_chip``, ``egsea``, and
``maker``. Until Galaxy offers something better, follow that idiom:

.. code-block:: xml

    <param name="non_commercial_use" type="boolean" checked="False"
           label="I certify that I am not using this tool for commercial purposes.">
      <validator type="expression" message="This tool is only available for non-commercial use.">value == True</validator>
    </param>

and back it with a defence-in-depth guard in ``<command>``, as the MEME macros
do:

.. code-block:: xml

    <token name="@CHECK_NON_COMMERCIAL_USE@"><![CDATA[
        #if not $non_commercial_use
            >&2 echo "this tool is only available for non commercial use";
            exit 1;
        #end if
    ]]></token>

Conventions worth holding to:

- **Name the parameter** ``non_commercial_use`` for a purpose certification.
  The repository is currently inconsistent — ``maker`` uses ``license_agreement``
  and ``clair3`` and ``artic_minion`` use ``ont_license_agree`` — which makes the
  pattern hard to find and hard to migrate later. Where the affirmation is
  acceptance of a *named* license rather than a statement about commercial
  purpose, a name derived from that license is reasonable, but be deliberate
  about it.
- **Put the affirmation last in** ``<inputs>``, so it reads as the final step
  before running. Most wrappers do; ``sfold`` puts it first.
- **Share it through a macro** across a suite. The five MEME wrappers share
  ``@CHECK_NON_COMMERCIAL_USE@`` but each carries its own copy of the parameter;
  the parameter belongs in the macro too.
- **Set it in every test**, and add a test that asserts the tool fails without
  it, as ``clair3`` does.
- **Do not assume CI will catch a missing gate.** ``planemo lint`` checks nothing
  on this page. The entire convention is enforced by human review.

Now the part that matters more than the idiom — **three things this pattern does
not do**:

1. **It is invisible when the tool runs inside a workflow.** A ``checked``
   boolean is not a runtime input; its value is baked into the workflow step at
   save time, so unless the workflow author deliberately exposes it as a runtime
   value, the run form never renders it. The workflow *author* affirmed on the
   runner's behalf, once, possibly years ago.
2. **The wrong thing persists.** No acceptance is recorded — nothing represents
   "this user accepted these terms", so there is no audit trail and nothing to
   revoke. Meanwhile the checkbox *value* persists in the places that skip the
   prompt on a later run: baked into workflow steps, as above, and reloaded
   pre-checked on rerun, since the tool form is repopulated from the previous
   job's parameters. A decision made once, for one purpose, already carries
   forward — invisibly, and with no record of who made it or when.
3. **It is a fake parameter.** It lands in the job's parameters, the tool state,
   the rerun form, API responses, and every workflow that embeds the tool. Six
   MEME-related wrappers each carry a separate affirmation about one license.

There is a fourth, quieter problem: consistency. PEAR carries the clearest
machine-readable non-commercial signal of any tool discussed here — its Bioconda
recipe uses the SPDX identifier ``CC-BY-NC-SA-3.0``, where MEME and Sfold fall
back to ``Custom`` and ``OTHER`` — and yet its wrapper has no affirmation at all,
only a note at the end of ``<help>``. Reasonable people have applied this idiom
to some tools and not others, which is what happens when the only available
mechanism is a convention rather than a declaration.
