"""
Logic for git remote discovery via ssh

The idea is to ssh into the remote and check to see if a git repo exists in a
similar location relative to the home directory and set that as the remote.
"""
from os.path import expanduser
from os.path import relpath
from git_sync.utils import _getcwd
import ubelt as ub


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


#####
def _devcheck():
    """
    TODO: need to resolve the  receive.denyCurrentBranch problem less manually

    remote: error: refusing to update checked out branch: refs/heads/updates
    remote: error: By default, updating the current branch in a non-bare repository
    remote: is denied, because it will make the index and work tree inconsistent
    remote: with what you pushed, and will require 'git reset --hard' to match
    remote: the work tree to HEAD.

    On the remote:

        git config --local receive.denyCurrentBranch warn

    """


def dvc_discover_ssh_remote(host, forward_ssh_agent=False,
                            dry=False):
    cwd = _getcwd()
    cwd = ub.Path(cwd)
    relcwd = relpath(cwd, expanduser('~'))

    # Build a list of places where the remote is likely to be located.
    candidate_remote_cwds = []
    candidate_remote_cwds.append(relcwd)

    # TODO: look at symlinks relative to home and try those but resolved?

    candidate_remote_cwds.append(cwd)
    candidate_remote_cwds.append(cwd.resolve())

    remote_cache_dir = None

    for remote_cwd in candidate_remote_cwds:
        # Build one command to execute on the remote
        remote_parts = [
            'cd {remote_cwd}',
        ]
        remote_parts.append('cd .git && pwd')
        ssh_flags = []
        if forward_ssh_agent:
            ssh_flags += ['-A']
        ssh_flags = ' '.join(ssh_flags)

        remote_part = ' && '.join(remote_parts)
        command_template = 'ssh {ssh_flags} {host} "' + remote_part + '"'
        kw = dict(
            host=host,
            remote_cwd=remote_cwd,
            ssh_flags=ssh_flags
        )
        command = command_template.format(**kw)
        print(command)
        info = ub.cmd(command, verbose=3)
        if info['ret'] == 0:
            remote_cache_dir = info['out'].strip().split('\n')[-1]
            print(f'remote_cache_dir={remote_cache_dir}')
            # remote_cache_dir = ub.Path(remote_cwd) / '.git'
            break
        else:
            print('Warning: Unable to find candidate DVC repo on the remote')

    if remote_cache_dir is None:
        raise Exception('No candidates were found')

    local_command = f'git remote add {host} ssh://{host}:{remote_cache_dir}'
    if not dry:
        # /media/joncrall/raid/home/joncrall/data/dvc-repos/smart_watch_dvc/.dvc/cache
        ub.cmd(local_command, verbose=3)
    else:
        print('Dry mode, would have run:')
        print(local_command)
