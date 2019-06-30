import click
import os
import os.path
from aim.commands.helpers import pass_aim_context
from cookiecutter.main import cookiecutter


@click.command('init', short_help='Initializes AIM Project files', help="""
Initializes AIM Project files. The types of resources possible are:

 - project: Create the skeleton configuration directory and files
        for an empty or complete AIM Project.

""")
@click.argument('config_type', default='project', type=click.STRING)
@pass_aim_context
def init_command(aim_ctx, config_type='project', region=None, keypair_name=None):
    """Initializes an AIM Project"""
    if config_type == 'project':
        print("\nAIM Project initialization")
        print("--------------------------\n")
        print("About to create a new AIM Project directory at {}\n".format(os.getcwd()))
        cookiecutter(os.path.dirname(__file__) + os.sep + 'aim-cookiecutter' + os.sep)
