#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import normpath
from os.path import realpath
from os.path import expanduser
from os.path import relpath
import os
import ubelt as ub


def _getcwd():
    """
    Workaround to get the working directory without dereferencing symlinks.
    This may not work on all systems.

    References:
        https://stackoverflow.com/questions/1542803/getcwd-dereference-symlinks
    """
    # TODO: use ubelt version if it lands
    canidate1 = os.getcwd()
    real1 = normpath(realpath(canidate1))

    # test the PWD environment variable
    candidate2 = os.getenv('PWD', None)
    if candidate2 is not None:
        real2 = normpath(realpath(candidate2))
        if real1 == real2:
            # sometimes PWD may not be updated
            return candidate2
    return canidate1


def git_sync(host, remote=None, message='wip', forward_ssh_agent=False, dry=False):
    """
    Commit any changes in the current working directory, ssh into a remote
    machine, and then pull those changes.

    Args:
        host (str):
            The name of the host to sync to: e.g. user@remote.com

        remote (str):
            The git remote used to push and pull from

        message (str, default='wip'):
            Default git commit message.

        forward_ssh_agent (bool):
            Enable forwarding of the ssh authentication agent connection

        dry (bool, default=False):
            Executes dry run mode.

    Example:
        >>> host = 'user@remote.com'
        >>> remote = 'origin'
        >>> message = 'this is the commit message'
        >>> git_sync(host, remote, message, dry=True)
        git commit -am "this is the commit message"
        git push origin
        ssh user@remote.com "cd ... && git pull origin"
    """
    cwd = _getcwd()
    relpwd = relpath(cwd, expanduser('~'))

    parts = [
        'git commit -am "{}"'.format(message),
    ]

    if remote:
        parts += [
            'git push {remote}',
            'ssh {host} "cd {relpwd} && git pull {remote}"'
        ]
    else:
        parts += [
            'git push',
            'ssh {ssh_flags} {host} "cd {relpwd} && git pull"'
        ]

    ssh_flags = []
    if forward_ssh_agent:
        ssh_flags += ['-A']
    ssh_flags = ' '.join(ssh_flags)

    kw = dict(host=host, relpwd=relpwd, remote=remote, ssh_flags=ssh_flags)

    for part in parts:
        command = part.format(**kw)
        if not dry:
            result = ub.cmd(command, verbose=2)
            retcode = result['ret']
            if command.startswith('git commit') and retcode == 1:
                pass
            elif retcode != 0:
                print('git-sync cannot continue. retcode={}'.format(retcode))
                break
        else:
            print(command)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Sync a git repo with a remote server via ssh')

    parser.add_argument('host', nargs=1, help='Server to sync to via ssh (e.g. user@servername.edu)')
    parser.add_argument('remote', nargs='?', help='The git remote to use (e.g. origin)')
    parser.add_argument('-A', dest='forward_ssh_agent', action='store_true',
                        help='Enable forwarding of the ssh authentication agent connection')
    parser.add_argument(*('-n', '--dry'), dest='dry', action='store_true',
                        help='Perform a dry run')
    parser.add_argument(*('-m', '--message'), type=str,
                        help='Specify a custom commit message')

    parser.set_defaults(
        dry=False,
        remote=None,
        message='wip',
    )
    args = parser.parse_args()
    ns = args.__dict__.copy()
    ns['host'] = ns['host'][0]

    git_sync(**ns)

if __name__ == '__main__':
    r"""
    CommandLine:
        python -m git_sync remote_host_name --dry
    """
    main()
