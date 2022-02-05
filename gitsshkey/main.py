import os
import hashlib
import pathlib

import click
from giturlparse import parse
from sshconf import read_ssh_config


class GitRepoType(click.ParamType):
    name = "repo"

    def convert(self, value, param, ctx):
        repo = parse(value)
        if not repo.valid:
            self.fail(f"{value!r} is not a valid git repo", param, ctx)
        return repo


GIT_REPO = GitRepoType()


DEFAULT_SSH_CONFIG = '.ssh/config'
DEFAULT_SSH_KEYS = '.ssh/'


_add_home = lambda p: pathlib.Path().home().joinpath(p).absolute().as_posix()
_hash_tag = lambda u: hashlib.sha256(u.encode()).hexdigest()[:7]


def make_alias(repo, tag):
    repo = parse(repo.url2ssh)
    repo._parsed['domain'] = repo.domain + '-' + tag
    alias_repo = parse(repo.url2ssh)
    if not alias_repo.valid:
        raise click.ClickException(f'git ssh url is not valid {repo.url2ssh}')
    return alias_repo


@click.command()
@click.option(
    '-c', '--config', 'config_file',
    type=click.Path(exists=True, dir_okay=False, file_okay=True, writable=True),
    help=f'ssh config file path, default is $HOME/{DEFAULT_SSH_CONFIG}',
    default=_add_home(DEFAULT_SSH_CONFIG))
@click.option(
    '--keys', 'keys',
    type=click.Path(exists=True, dir_okay=True, file_okay=False, writable=True),
    help=f'ssh keys file path, default is $HOME/{DEFAULT_SSH_KEYS}',
    default=_add_home(DEFAULT_SSH_KEYS))
@click.argument('repo', type=GIT_REPO)
def main(repo, keys, config_file):
    '''
    REPO    git repo link https/ssh/git
    '''
    config = read_ssh_config(config_file)

    tag = _hash_tag(repo.url2ssh)
    alias_repo = make_alias(repo, tag)
    if alias_repo.domain in config.hosts():
        # TODO: add echo
        return

    key_file = f'{alias_repo.domain}.id_rsa'
    key_path = pathlib.Path(keys).joinpath(key_file)

    public_key_file = key_file + '.pub'
    public_key_path = pathlib.Path(keys).joinpath(public_key_file)
    if key_path.exists() or public_key_path.exists():
        # TODO: add echo
        return

    # generate key
    comment = f'key for {alias_repo.url2ssh}'
    cmd = f'ssh-keygen -t rsa -b 2048 -C "{comment}" -f {key_path.as_posix()} -q -N ""'
    flag = os.system(cmd)
    if flag != 0:
        # TODO: add echo
        return

    # save to config
    config.add(alias_repo.domain, Hostname=repo.domain, User=repo.user, IdentityFile=key_path.as_posix())
    config.save()

    # show
    click.echo(f'New repo address: {click.style(alias_repo.url2ssh, fg="green")}')
    click.echo(f'New repo public rsa key: {click.style(public_key_path, fg="green")}')
