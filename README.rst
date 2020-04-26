The git_sync Module
===================

|CircleCI| |Travis| |Appveyor| |Codecov| |Pypi| |Downloads| |ReadTheDocs|

The ``git_sync`` module.

+------------------+----------------------------------------------+
| Read the docs    | https://git_sync.readthedocs.io              |
+------------------+----------------------------------------------+
| Github           | https://github.com/Erotemic/git_sync         |
+------------------+----------------------------------------------+
| Pypi             | https://pypi.org/project/git_sync            |
+------------------+----------------------------------------------+


This is a very simple git script to help with local development and remote
execution. It turns the process of commiting, logging into the remote machine,
and then pulling on the remote machine into a single command.

Assuming that you have the same file structure on both your local and remote
machine, `git-sync` allows you to edit files locally, and when you want those 
changes reflected on the remote machine, you execute 

```bash
git-sync other-machine
```

This performs the following actions:

1. Executes a git commit to the local repo (the default commit message is "wip",
   but this can be changed using the -m flag). 

2. Executes a `git push origin` which pushes the local copy of the repo to the
   git server. (Note, git-sync defaults to the origin git remote, but you can
   specify a different one using a second positional argument: e.g. 
   `git-sync other-machine remote2`).

3. Creates an SSH connection to "other-machine", cd's into the same directory
   you are in on the local machine (which is why mirroring the directory
   structure across development machines is important), and then executes a
   `git pull origin`, which will update the remote machine to the newly pushed
   state. 


Note that this script is very simple, it will fail if these conditions aren't met.

* The location of the repo (relative to the home directory) must be the same on
  the local and remote machine. Note, it is fairly easy to ensure this is the
  case using symlinks.

* The repo on the local machine and remote machine must be on the same branch.

* The repo on the remote machine must be in a clean state.


.. |Pypi| image:: https://img.shields.io/pypi/v/git_sync.svg
   :target: https://pypi.python.org/pypi/git_sync

.. |Downloads| image:: https://img.shields.io/pypi/dm/git_sync.svg
   :target: https://pypistats.org/packages/git_sync

.. |ReadTheDocs| image:: https://readthedocs.org/projects/git_sync/badge/?version=release
    :target: https://git_sync.readthedocs.io/en/release/

.. # See: https://ci.appveyor.com/project/jon.crall/git_sync/settings/badges
.. |Appveyor| image:: https://ci.appveyor.com/api/projects/status/py3s2d6tyfjc8lm3/branch/master?svg=true
   :target: https://ci.appveyor.com/project/jon.crall/git_sync/branch/master

.. |CircleCI| image:: https://circleci.com/gh/Erotemic/git_sync.svg?style=svg
    :target: https://circleci.com/gh/Erotemic/git_sync

.. |Travis| image:: https://img.shields.io/travis/Erotemic/git_sync/master.svg?label=Travis%20CI
   :target: https://travis-ci.org/Erotemic/git_sync

.. |Codecov| image:: https://codecov.io/github/Erotemic/git_sync/badge.svg?branch=master&service=github
   :target: https://codecov.io/github/Erotemic/git_sync?branch=master
