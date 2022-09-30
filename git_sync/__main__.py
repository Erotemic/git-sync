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


def git_default_push_remote_name():
    local_remotes = ub.cmd('git remote -v')['out'].strip()
    lines = [line for line in local_remotes.split('\n') if line]
    candidates = []
    for line in lines:
        parts = line.split('\t')
        remote_name, remote_url_type = parts
        if remote_url_type.endswith('(push)'):
            candidates.append(remote_name)
    if len(candidates) == 1:
        remote_name = candidates[0]
    return remote_name


def git_sync(host, remote=None, message='wip [skip ci]', forward_ssh_agent=False,
             dry=False, force=False):
    """
    Commit any changes in the current working directory, ssh into a remote
    machine, and then pull those changes.

    Args:
        host (str):
            The name of the host to sync to: e.g. user@remote.com

        remote (str):
            The git remote used to push and pull from

        message (str, default='wip [skip ci]'):
            Default git commit message.

        forward_ssh_agent (bool):
            Enable forwarding of the ssh authentication agent connection

        force (bool, default=False):
            if True does a forced push and additionally forces the remote to do
            a hard reset to the remote state.

        dry (bool, default=False):
            Executes dry run mode.

    Example:
        >>> host = 'user@remote.com'
        >>> remote = 'origin'
        >>> message = 'this is the commit message'
        >>> git_sync(host, remote, message, dry=True)
        git commit -am "this is the commit message"
        git push origin
        ssh user@remote.com "cd ... && git pull origin ..."
    """
    cwd = _getcwd()
    relcwd = relpath(cwd, expanduser('~'))

    """
    # How to check if a branch exists
    git branch --list ${branch}

    # Get current branch name

    if [[ "$(git rev-parse --abbrev-ref HEAD)" != "{branch}" ]];
        then git checkout {branch} ;
    fi

    # git rev-parse --abbrev-ref HEAD
    if [[ -z $(git branch --list ${branch}) ]]; then
    else
    fi
    """

    # $(git branch --list ${branch})

    # Assume the remote directory is the same as the local one (relative to home)
    remote_cwd = relcwd

    # Build one command to execute on the remote
    remote_parts = [
        'cd {remote_cwd}',
    ]

    # Get branch name from the local
    local_branch_name = ub.cmd('git rev-parse --abbrev-ref HEAD')['out'].strip()
    # Assume the branches are the same between local / remote
    remote_branch_name = local_branch_name

    if force:
        if remote is None:
            # FIXME: might not work in all cases
            remote = git_default_push_remote_name()

        # Force the remote to the state of the remote
        remote_checkout_branch_force = ub.paragraph(
            '''
            git fetch {remote};
            if [[ "$(git rev-parse --abbrev-ref HEAD)" != "{branch}" ]]; then
                git checkout {branch};
            fi;
            git reset {remote}/{branch} --hard
            ''').format(
                remote=remote,
                branch=remote_branch_name
            )

        remote_parts += [
            'git fetch {remote}',
            remote_checkout_branch_force.replace('"', r'\"'),
        ]
    else:
        # ensure the remote is on the right branch
        # (this assumes no conflicts and will fail if anything bad
        #  might happen)
        remote_checkout_branch_simple = ub.paragraph(
            r'''
            if [[ "$(git rev-parse --abbrev-ref HEAD)" != "{branch}" ]]; then
                git checkout {branch};
            fi
            ''').format(branch=local_branch_name)

        remote_parts += [
            'git pull {remote}' if remote else 'git pull',
            remote_checkout_branch_simple.replace('"', r'\"'),
        ]

    remote_part = ' && '.join(remote_parts)

    # Build one comand to execute locally
    commit_command = 'git commit -am "{}"'.format(message)

    push_args = ['git push']
    if remote:
        push_args.append('{remote}')
    if force:
        push_args.append('--force')
    push_command = ' '.join(push_args)

    sync_command = 'ssh {ssh_flags} {host} "' + remote_part + '"'

    local_parts = [
        commit_command,
        push_command,
        sync_command,
    ]

    ssh_flags = []
    if forward_ssh_agent:
        ssh_flags += ['-A']
    ssh_flags = ' '.join(ssh_flags)

    kw = dict(
        host=host,
        remote_cwd=remote_cwd,
        remote=remote,
        ssh_flags=ssh_flags
    )

    for part in local_parts:
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
    parser.add_argument('--force', default=False, action='store_true',
                        help='Force push and hard reset the remote.')

    parser.set_defaults(
        dry=False,
        remote=None,
        message='wip [skip ci]',
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
