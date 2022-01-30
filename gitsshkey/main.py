import pathlib

import click
from giturlparse import parse


class GitRepoType(click.ParamType):
    name = "repo"

    def convert(self, value, param, ctx):
        repo = parse(value)
        if not repo.valid:
            self.fail(f"{value!r} is not a valid git repo", param, ctx)
        return repo


GIT_REPO = GitRepoType()


DEFAULT_SSH_CONFIG = '.ssh/config'
DEFAULT_SSH_KEYS = '.ssh/keys/'


_add_home = lambda p : pathlib.Path().home().joinpath(p).absolute().as_posix()


@click.command()
@click.option('-c', '--config', 'ssh_config',
    type=click.Path(exists=True, dir_okay=False, file_okay=True, writable=True),
    help=f'ssh config file path, default is $HOME/{DEFAULT_SSH_CONFIG}',
    default=_add_home(DEFAULT_SSH_CONFIG))
@click.option('--keys', 'keys',
    type=click.Path(exists=True, dir_okay=True, file_okay=False, writable=True),
    help=f'ssh keys file path, default is $HOME/{DEFAULT_SSH_KEYS}',
    default=_add_home(DEFAULT_SSH_KEYS))
@click.argument('repo', type=GIT_REPO)
def main(repo, keys, ssh_config):
    '''
    REPO    git repo https/ssh/git
    '''
    click.echo(repo)
    click.echo(keys)
    click.echo(ssh_config)
    click.secho(repo.url2ssh, fg='green')
