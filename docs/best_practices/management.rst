Repository Management on GitHub and the ToolShed
================================================

Manual Management
-----------------

For smaller groups, manual management of your repositories may be sufficient.
The IUC strongly recommends the use of Planemo for uploading tools. This is as
simple as defining your ``~/.planemo.yml`` and running ``planemo shed_upload
-m "We added new feature X" path/to/my/repo``.

Automated Management
--------------------

The IUC has developed github actions configurations in order to assist in
continually synchronizing your GitHub repository with the toolshed components.
You can view these in `.github/workflows in the IUC's Github Repo <https://github.com/galaxyproject/tools-iuc/blob/master/.github/workflows>`__
