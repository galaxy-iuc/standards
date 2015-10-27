Packages
========

Before you start writing a new tool please search the `Main Tool Shed
(MTS) <https://toolshed.g2.bx.psu.edu>`__ and the `Test Tool Shed
(TTS) <https://testtoolshed.g2.bx.psu.edu>`__ because it's possible that
someone has already created an installer for the same third party
executable you are looking for. Consider announcing your packaging project on
galaxy-dev to see if anyone has already created a wrapper.

Packaging software is something of a more advanced topic, and due to the
complexities of the syntax, somewhat harder to validate.


Downloads
---------

Packages generally must download one or more files from the internet in order
to function. We require checksums on all of our package downloads from multiple reasons:

-  Download integrity.
-  Insecure transport methods, like ``http://`` and ``ftp://``
-  The packages come from the untrusted internet, we don't know if anyone has
   modified the software in transit. This software is installed directly to
   large university clusters. We must make an effort to ensure that what is
   being installed is what the user actually asked for, and not a version of
   ``bowtie`` that has been modified unexpectedly.

The checksums take the form of sha256sums attached as attributes to
``<action type="download_by_url">`` and other elements, e.g.

.. code:: xml

    <action type="download_by_url" sha256sum="ab060325...">
         http://mbio-serv2.mbioekol.lu.se/ARAGORN/Downloads/aragorn1.2.36.tgz
    </action>

This XML snippet will cause the file ``aragorn1.2.36.tgz`` to be downloaded,
and to be validated. If the sha256sums match, then the package installs.
Otherwise, it fails immediately.
