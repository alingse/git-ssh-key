import os
import hashlib
import pathlib

import click
from giturlparse import parse
from sshconf import empty_ssh_config_file, read_ssh_config


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


_add_home = lambda p: pathlib.Path().home().joinpath(p).absolute().resolve().as_posix()
_hash_tag = lambda u: hashlib.sha256(u.encode()).hexdigest()[:7]

_green = lambda t: click.style(t, fg="green")
_red = lambda t: click.style(t, fg="red")


def make_alias(repo, tag):
    repo = parse(repo.url2ssh)
    repo._parsed['domain'] = repo.domain + '-' + tag
    alias_repo = parse(repo.url2ssh)
    if not alias_repo.valid:
        raise click.ClickException(f'git ssh url is not valid {repo.url2ssh}')
    return alias_repo


def make_key_path(keys, alias_repo):
    keys_path = pathlib.Path(keys).absolute().resolve()

    private_key_file = f'{alias_repo.domain}.id_rsa'
    public_key_file = f'{private_key_file}.pub'
    private_key_path = keys_path.joinpath(private_key_file).absolute().resolve()
    public_key_path = keys_path.joinpath(public_key_file).absolute().resolve()
    if private_key_path.exists() or public_key_path.exists():
        click.echo(f'key file {_red(private_key_path)} or public key file {_red(public_key_path)} already exists.')
        raise click.Abort()
    return private_key_path, public_key_path


def generate_key(private_key_path, alias_repo):
    cmd = f'ssh-keygen -t rsa -b 2048 -C "key for {alias_repo.url2ssh}" -f {private_key_path.as_posix()} -q -N ""'
    flag = os.system(cmd)
    if flag != 0:
        click.echo(f'run command {_red(cmd)} failed.')
        raise click.Abort()


@click.command()
@click.option(
    '-c', '--config', 'config_file',
    type=click.Path(dir_okay=False, file_okay=True, writable=True),
    help=f'ssh config file path, default is $HOME/{DEFAULT_SSH_CONFIG}',
    default=_add_home(DEFAULT_SSH_CONFIG))
@click.option(
    '--keys', 'keys',
    type=click.Path(exists=True, dir_okay=True, file_okay=False, writable=True),
    help=f'ssh keys file path, default is $HOME/{DEFAULT_SSH_KEYS}',
    default=_add_home(DEFAULT_SSH_KEYS))
@click.option(
    '-t', '--tag', 'tag',
    type=str, help='alias tag add to host default is hash(url)')
@click.argument('repo', type=GIT_REPO)
def main(repo, tag, keys, config_file):
    '''
    REPO    git repo link( https/ssh/git )
    '''
    if pathlib.Path(config_file).exists():
        config = read_ssh_config(config_file)
        save_config = lambda: config.save
    else:
        config = empty_ssh_config_file()
        save_config = lambda: config.write(config_file)

    if not tag:
        tag = _hash_tag(repo.url2ssh)
    alias_repo = make_alias(repo, tag)
    # check
    if alias_repo.domain in config.hosts():
        click.echo(f'alias repo already added in ssh config')
        click.echo(f'alias repo address: {_green(alias_repo.url2ssh)}')
        return

    # generate key
    private_key_path, public_key_path = make_key_path(keys, alias_repo)
    generate_key(private_key_path, alias_repo)

    # save config
    config.add(
        alias_repo.domain,
        Hostname=repo.domain,
        User=repo.user,
        IdentityFile=private_key_path.as_posix())
    save_config()

    # show
    click.echo(f'alias repo address: {_green(alias_repo.url2ssh)}')
    click.echo(f'alias repo public rsa key: {_green(public_key_path)}')
