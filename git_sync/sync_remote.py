from os.path import expanduser
from os.path import relpath
import ubelt as ub
from git_sync.utils import _getcwd


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


def git_sync(host, remote=None, message='wip [skip ci]',
             forward_ssh_agent=False, dry=False, force=False, home=None):
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

        home (str | PathLike | None):
            if specified, overwrite where git-sync thinks the home location is

    Example:
        >>> # xdoctest: +IGNORE_WANT
        >>> from git_sync.sync_remote import *  # NOQA
        >>> from git_sync.sync_remote import git_sync, _getcwd
        >>> host = 'user@remote.com'
        >>> remote = 'origin'
        >>> message = 'this is the commit message'
        >>> home = _getcwd()  # pretend the home is here for the test
        >>> git_sync(host, remote, message, dry=True, home=home)
        git commit -am "this is the commit message"
        git push origin
        ssh user@remote.com "cd ... && git pull origin ..."
    """
    cwd = _getcwd()
    if home is None:
        home = expanduser('~')
    try:
        relcwd = relpath(cwd, home)
    except ValueError:
        raise ValueError((
            'git-sync assumes that you are running relative '
            'to your home directory. cwd={}, home={}').format(cwd, home))

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
    remote_parts = []

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

        if remote == host:
            # If the remote is also the host, then we have to do things
            # differently.
            remote_parts += [
                remote_checkout_branch_simple.replace('"', r'\"'),
                'git reset --hard HEAD'
            ]
        else:
            remote_parts += [
                'git pull {remote}' if remote else 'git pull',
                remote_checkout_branch_simple.replace('"', r'\"'),
            ]

    # Build one comand to execute locally
    commit_command = 'git commit -am "{}"'.format(message)

    push_args = ['git push']
    if remote:
        push_args.append(f'{remote}')
    if force:
        push_args.append('--force')
    push_command = ' '.join(push_args)

    ssh_flags = []
    if forward_ssh_agent:
        ssh_flags += ['-A']
    ssh_flags = ' '.join(ssh_flags)

    sync_command = _build_remote_command(
        ' && '.join(remote_parts), remote_cwd, ssh_flags, host)

    local_commands = [
        ('commit', commit_command),
        ('push', push_command),
        ('sync', sync_command),
    ]

    for part_name, command in local_commands:
        if not dry:
            result = ub.cmd(command, verbose=3)
            retcode = result['ret']
            if command.startswith('git commit') and retcode == 1:
                pass
            elif retcode != 0:
                if part_name == 'push':
                    if 'updating the current branch in a non-bare repo' in result['err']:
                        from rich.prompt import Confirm
                        # We can handle this case if the user wants to
                        if Confirm.ask('Do you want to force this?'):
                            fix_command = _build_remote_command(
                                'git config --local receive.denyCurrentBranch warn',
                                remote_cwd, ssh_flags, host)
                            result = ub.cmd(fix_command, verbose=3)
                            retcode = result['ret']
                            if retcode == 0:
                                # Retry after running the fix
                                result = ub.cmd(command, verbose=3)
                                retcode = result['ret']
                                if retcode == 0:
                                    continue

                print('git-sync cannot continue. retcode={}'.format(retcode))
                break
        else:
            print(command)


def _build_remote_command(command, remote_cwd, ssh_flags, host):
    remote_parts = [
        f'cd {remote_cwd}',
        command
    ]
    remote_part = ' && '.join(remote_parts)
    local_part = f'ssh {ssh_flags} {host} "' + remote_part + '"'
    return local_part
