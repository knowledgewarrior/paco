import aim.models
import click
import sys
from aim.commands.helpers import controller_args, aim_home_option, init_aim_home_option, pass_aim_context, \
    handle_exceptions, controller_types
from aim.core.exception import StackException


@click.command(name='provision', short_help='Provision resources to the cloud.')
@controller_args
@aim_home_option
@pass_aim_context
@handle_exceptions
def provision_command(aim_ctx, controller_type, arg_1=None, arg_2=None, arg_3=None, arg_4=None, home='.'):
    """Provision AWS Resources"""
    aim_ctx.command = 'provision'
    init_aim_home_option(aim_ctx, home)
    if not aim_ctx.home:
        print('AIM configuration directory needs to be specified with either --home or AIM_HOME environment variable.')
        sys.exit()

    aim_ctx.log("Provision: Controller: {}  arg_1({}) arg_2({}) arg_3({}) arg_4({})".format(controller_type, arg_1, arg_2, arg_3, arg_4) )
    aim_ctx.load_project()

    controller_args = {
        'command': 'provision',
        'arg_1': arg_1,
        'arg_2': arg_2,
        'arg_3': arg_3,
        'arg_4': arg_4
    }
    controller = aim_ctx.get_controller(controller_type, controller_args)
    controller.provision()

provision_command.help = """
Provision AWS Resources.

CONTROLLER_TYPE can be one of:

""" + controller_types