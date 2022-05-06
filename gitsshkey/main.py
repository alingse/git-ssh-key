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


_add_home = lambda p: pathlib.Path().home().joinpath(p).absolute().resolve()
_hash_tag = lambda u: hashlib.sha256(u.encode()).hexdigest()[:7]

_green = lambda t: click.style(str(t), fg="green")
_red = lambda t: click.style(str(t), fg="red")


if _add_home('.ssh/').exists():
    DEFAULT_SSH_CONFIG = '.ssh/config'
    DEFAULT_SSH_KEYS = '.ssh/'
else:
    DEFAULT_SSH_CONFIG = 'git-ssh-key.config'
    DEFAULT_SSH_KEYS = ''


def make_alias(repo, tag):
    repo = parse(repo.url2ssh)
    repo._parsed['domain'] = repo.domain + '-' + tag
    alias_repo = parse(repo.url2ssh)
    if not alias_repo.valid:
        raise click.ClickException(f'git ssh url is not valid {repo.url2ssh}')
    return alias_repo


def get_or_create_config(config_file):
    if pathlib.Path(config_file).exists():
        config = read_ssh_config(config_file)
        save_config = lambda: config.save()
    else:
        config = empty_ssh_config_file()
        save_config = lambda: config.write(config_file)
    return config, save_config


def generate_key(key_path, alias_repo):
    cmd = f'ssh-keygen -t rsa -b 2048 -C "key for {alias_repo.url2ssh}" -f {key_path.as_posix()} -q -N ""'
    flag = os.system(cmd)
    if flag != 0:
        click.echo(f'run command {_red(cmd)} failed.')
        raise click.Abort()


def get_or_create_key(key, keys, alias_repo):
    if key:
        key_path = pathlib.Path(key).absolute().resolve()
    else:
        key_file = f'{alias_repo.domain}.id_rsa'
        key_path = pathlib.Path(keys).joinpath(key_file).absolute().resolve()
        if not key_path.exists():
            generate_key(key_path, alias_repo)

    public_key_path = pathlib.Path(key_path.as_posix() + '.pub')
    if not public_key_path.exists():
        click.echo(f'public key path {_red(public_key_path)} not exists')
        raise click.Abort()

    return key_path, public_key_path


@click.command()
@click.option(
    '-c', '--config', 'config_file',
    type=click.Path(dir_okay=False, file_okay=True, writable=True),
    help=f'ssh config file path, default is $HOME/{DEFAULT_SSH_CONFIG}',
    default=_add_home(DEFAULT_SSH_CONFIG).as_posix())
@click.option(
    '--keys', 'keys',
    type=click.Path(exists=True, dir_okay=True, file_okay=False, writable=True),
    help=f'new generate ssh key\'s path, default is $HOME/{DEFAULT_SSH_KEYS}',
    default=_add_home(DEFAULT_SSH_KEYS).as_posix())
@click.option(
    '-k', '--key', 'key',
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help=f'ssh private key file, if not provide, will auto generate a new key into `--keys`')
@click.option(
    '-t', '--tag', 'tag',
    type=str,
    help='alias tag add to host default is hash(url)')
@click.argument('repo', type=GIT_REPO)
def main(repo, tag, key, keys, config_file):
    '''
    REPO    git repo link( https/ssh/git )
    '''
    if tag is None:
        tag = _hash_tag(repo.url2ssh)
    alias_repo = make_alias(repo, tag)

    # config
    config, save_config = get_or_create_config(config_file)

    # check if exists.
    if alias_repo.domain in config.hosts():
        click.echo(f'alias repo already added in ssh config')
        click.echo(f'alias repo address: {_green(alias_repo.url2ssh)}')
        return

    # get or create key
    key_path, public_key_path = get_or_create_key(key, keys, alias_repo)

    # save config
    config.add(
        alias_repo.domain,
        Hostname=repo.domain,
        User=repo.user,
        IdentityFile=key_path.as_posix())
    save_config()

    # show
    click.echo(f'alias repo address: {_green(alias_repo.url2ssh)}')
    click.echo(f'alias repo public rsa key: {_green(public_key_path)}')
