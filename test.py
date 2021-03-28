import click

class Config(object):
    def __init__(self):
        self.verbose = False

pass_config = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.option('--verbose', is_flag=True)
@click.option('--home-dir', type=click.Path())
@pass_config
def cli(config, verbose, home_dir):
    config.verbose = verbose
    if home_dir is None:
        home_dir = '.'
    config.home_dir = home_dir

@cli.command()
@pass_config
@click.option('--string', default='World', help="This is the thing im greeting.")
def say(config, string):
    """This script greets you."""
    if config.verbose:
        click.echo('Running command in verbose mode')

    click.echo('Home directory is {}'.format(config.home_dir))

    click.echo('Hello {}'.format(string))