#!/usr/bin/env python
# -*- coding: utf-8 -*-


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

    from git_sync.core import git_sync
    git_sync(**ns)

if __name__ == '__main__':
    r"""
    CommandLine:
        python -m git_sync remote_host_name --dry
    """
    main()
