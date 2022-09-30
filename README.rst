The git_sync Module
===================

.. |Travis| |Codecov| |Pypi| |Downloads| 
|GithubActions| |ReadTheDocs| |Pypi| |Downloads| |Codecov| 

The ``git_sync`` module.

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

.. code:: 

    git-sync other-machine


Note, that **this creates a commit** with the message "wip" and pushes it to
the default git-remote. The commit message and target git-remote can be
modified by command line args.


Installation
------------

Installing the git_sync Python module also installs the ``git-sync`` command line utility.

.. code:: 

    pip install git-sync


Details
-------

Executing ``git-sync`` performs the following actions:

1. Executes a git commit to the local repo (the default commit message is "wip",
   but this can be changed using the -m flag). 

2. Executes a ``git push origin`` which pushes the local copy of the repo to the
   git server. (Note, git-sync defaults to the origin git remote, but you can
   specify a different one using a second positional argument: e.g. 
   ``git-sync other-machine remote2``).

3. Creates an SSH connection to "other-machine", cd's into the same directory
   you are in on the local machine (which is why mirroring the directory
   structure across development machines is important), and then executes a
   ``git pull origin``, which will update the remote machine to the newly pushed
   state. 


Caveats
-------

Note that this script is very simple, it will fail if these conditions aren't met.

* The location of the repo (relative to the home directory) must be the same on
  the local and remote machine. Note, it is fairly easy to ensure this is the
  case using symlinks.

* The repo on the local machine and remote machine must be on the same branch.

* The repo on the remote machine must be in a clean state.


On SSH Configs
--------------

Also, to make life easier, it is best that you have a $HOME/.ssh/config file
setup with the remote machines you to access and appropriate identify files so
you don't need to enter your password each time you ``git-sync``.

An example ssh config entry is:

.. code:: 

    Host {myremote} {myremote.com}
        HostName {myremote.com}
        Port 22
        User {username}
        identityfile ~/.ssh/{my_id_ed25519}

Replacing any entry in ``{curly braces}`` with an appropriate value. 


If you don't have an ssh identify file, create one using:

.. code:: 

    mkdir -p $HOME/.ssh
    cd $HOME/.ssh

    FPATH="$HOME/.ssh/my_id_ed25519"
    ssh-keygen -t ed25519 -b 256 -C "${EMAIL}" -f $FPATH -N ""

    chmod 700 ~/.ssh
    chmod 400 ~/.ssh/id_*
    chmod 644 ~/.ssh/id_*.pub


And ensure the public key is registered with the remote machine:

.. code:: 

    REMOTE={myremote.com}
    REMOTE_USER={myusername}
    ssh-copy-id $REMOTE_USER@$REMOTE


Similar Software
----------------

* `CFarm  <https://github.com/robertmaynard/cfarm>`__ is a tool for keeping remotes in sync and testing code on the remote machines. 

* `Visual Studio Code <https://code.visualstudio.com/>`__ has great remote ssh and developing support. 


.. |CircleCI| image:: https://circleci.com/gh/Erotemic/git_sync.svg?style=svg
    :target: https://circleci.com/gh/Erotemic/git_sync

.. |Codecov| image:: https://codecov.io/github/Erotemic/git_sync/badge.svg?branch=main&service=github
   :target: https://codecov.io/github/Erotemic/git_sync?branch=main

.. |Pypi| image:: https://img.shields.io/pypi/v/git_sync.svg
   :target: https://pypi.python.org/pypi/git_sync

.. |Downloads| image:: https://img.shields.io/pypi/dm/git_sync.svg
   :target: https://pypistats.org/packages/git_sync

.. |ReadTheDocs| image:: https://readthedocs.org/projects/git_sync/badge/?version=latest
    :target: http://git_sync.readthedocs.io/en/latest/

.. |GithubActions| image:: https://github.com/Erotemic/git_sync/actions/workflows/tests.yml/badge.svg?branch=main
    :target: https://github.com/Erotemic/git_sync/actions?query=branch%3Amain
