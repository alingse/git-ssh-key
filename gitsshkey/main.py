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


@click.command()
@click.option('-c', '--config', 'config_file',
    type=click.Path(exists=True, dir_okay=False, file_okay=True, writable=True),
    help=f'ssh config file path, default is $HOME/{DEFAULT_SSH_CONFIG}',
    default=_add_home(DEFAULT_SSH_CONFIG))
@click.option('--keys', 'keys',
    type=click.Path(exists=True, dir_okay=True, file_okay=False, writable=True),
    help=f'ssh keys file path, default is $HOME/{DEFAULT_SSH_KEYS}',
    default=_add_home(DEFAULT_SSH_KEYS))
@click.argument('repo', type=GIT_REPO)
def main(repo, keys, config_file):
    '''
    REPO    git repo https/ssh/git
    '''
    config = read_ssh_config(config_file)

    # domain-hash
    domain = repo.domain
    tag = _hash_tag(repo.url2ssh)
    domain_tag = domain + '-' + tag
    if domain_tag in config.hosts():
        return

    key_file = f'{domain_tag}.id_rsa'
    key_path = pathlib.Path(keys).joinpath(key_file)
    public_key_file = key_file + '.pub'
    public_key_path = pathlib.Path(keys).joinpath(public_key_file)
    if key_path.exists() or public_key_path.exists():
        return

    # generate key
    comment = f'{domain_tag} for {repo.url2ssh}'
    cmd = f'ssh-keygen -t rsa -b 2048 -C "{comment}" -f {key_path.as_posix()} -q -N ""'
    flag = os.system(cmd)
    if flag != 0:
        return

    # add config
    config.add(domain_tag, Hostname=domain, User=repo.user, IdentityFile=key_path.as_posix())
    config.save()

    # update && show
    repo._parsed['domain'] = domain_tag
    url = repo.url2ssh
    click.echo(f'New repo address: {click.style(url, fg="green")}')
    click.echo(f'New repo public rsa key: {click.style(public_key_path, fg="green")}')
