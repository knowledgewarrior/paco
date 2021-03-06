.. _started:

Getting Started with Paco
=========================

Once you have the `paco` command-line installed, to get up and running you will need to:

  1. Create a Paco project.

  2. Create an IAM User and Role in your AWS account.

  3. Connect your Paco project with your IAM User and Role.


Create a Paco project
----------------------

The ``paco init`` command is there to help you get started with a new Paco project.
It will let you create a new Paco project from a template and connect that project
to your AWS account(s).

First you will use the ``paco init project`` command to create a new project. This
command takes as a single arguement the name of directory to create with your
new Paco project files. Run it with:

.. code-block:: bash

  $ paco init project <my-paco-project>

You will be presented with a series of questions about your new project.

You will be asked to supply some ``name`` and ``title`` values. Paco makes an important distinction
between a ``name`` field and a ``title`` field. The ``name`` fields are used to construct unique
resource names in AWS, while ``title`` is for human-readable descriptions.

.. Note:: **Name guidelines in Paco**

    1. AWS resources have different character set restrictions.
        We recommend using only alphanumeric charcters and the hyphen character in names (a-zA-Z-).

    2. Try to limit names to only 3 to 5 characters.
        Paco ``name`` fields are concatenated together to create unique names. Certain AWS resources names
        are limited to only 32 characters. If you use long names they may be too long for AWS.

    3. Names can not be changed after they provsion AWS resources.
        Names identify resources in AWS. Once you use Paco to create resources in AWS, if you
        change ``name`` fields Paco will no longer know where those resources are. The only way
        to change a ``name`` field is to delete the resources, change the name, and create new ones.

An example set of answers for creating a Paco project:

.. code-block:: bash

    project_title: My Paco Project
    network_environment_name: ne
    network_environment_title: My Paco Network
    application_name: app
    application_title: My Application
    aws_default_region: us-west-2
    master_account_id: 123456789012
    master_root_email: you@example.com

After this you will have a new directory of files that comprises and Paco project.

The path to this Paco Project directory is called your PACO home. The rest of the commands
you run will need this path supplied with the `--home` CLI option. For macos and linux users,
there is also a file named `profile.sh` which will export an `PACO_HOME`
environment variable to your shell. This environment variable can be used to make it easier
by avoiding the need to type out the `--home` option for every command:

.. code-block:: bash

  $ source my-paco-project/profile.sh
  (My AWS Paco Project) laptop username$


Create a User and Role in your AWS account
------------------------------------------

When you run Paco it will requrie access to your AWS account.

Paco requires access key credentials for an IAM User that has permissions to switch
to an IAM Role that delegates full Administrator access.


.. Note::

  Why can't I just use any AWS Access Key with Administrator access with Paco?

  Paco requires an IAM User capable of switching to a Role that contains Administrator permissions.
  Paco does this for security reasons. Paco will ask you for your MFA token from the CLI.
  As you store an AWS Access Key and Secret in a Paco ``.credentials`` file, if this file is accidentaly leaked
  then unwanted users will not be able to use your key without also being able to access your MFA device.

To install a CloudFormation template that will create a User and Role to use with Paco.

  1. Click on `this URL to create a PacoAdminAccess CloudFormation stack`_ in your AWS Account.

     .. image:: _static/images/create-paco-admin-stack.png

  #. Click "Next" and take note that you will create a IAM User with the name ``paco-admin``.
     If you like you can change this username here.

     .. image:: _static/images/stack-admin-username.png

  #. On the "Configure stack options" screen you can leave everything default and click "Next".
     On the "Review PacoInitialization" you can also leave all the defaults click
     "I acknowledge that AWS CloudFormation might create IAM resources with custom names."
     to confirm that this stack can create an IAM User.
     Finally click "Create stack".

.. _this URL to create a PacoAdminAccess CloudFormation stack: https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=PacoAdminAccess&templateURL=https://paco-cloud.s3-us-west-2.amazonaws.com/PacoInitialization.yaml

Create an AWS Access Key and configure MFA
------------------------------------------

Next you will need to set-up the new User account with an API key:

  1. In the AWS Console, go to the Identity and Access Management (IAM) Service, click on "Users"
     and click on the User name you supplied earlier. Then click on the "Security credentials" tab.

     .. image:: _static/images/quickstart101-user-start.png

  #. Set-up multi-factor authentication (MFA). Where it says, "Assigned MFA device" click on "Manage".
     Choose "Virtual MFA device" and use either Authy_ or `Google Authenticator`_ on your computer or phone
     as a virtual MFA device.

  #. Create an AWS Access Key. While still on the "Security credentials" tab, click on "Create access key".
     You will be given an "Access key ID" and "Secret access key". Copy these and you will use them
     to configure your Paco credentials next.

.. Note::

    If you no longer want to use Paco, you can go to CloudFormation and delete the stack that you created.
    However, before you delete the stack, you will need to return to this user and manually delete the
    Assigned MFA Device and Access key. If you try and delete the stack without doing this first, you will get the
    error message "DELETE_FAILED: Cannot delete entity, must delete MFA device first.".

Connect your Paco project with your AWS account
-----------------------------------------------

Next use the ``paco init credentials`` command to initialize your credentials. Enter the name of your IAM User
if you used the CloudFormation template your role name will be ``Paco-Admin-Delegate-Role``.

.. code-block:: bash

    $ paco init credentials --home=/path/to/your-paco-project

    Paco project credentials initialization
    ---------------------------------------

    Paco Admin Username: [paco-admin]:
    AWS Access Key: KAKIA***********4MXP
    AWS Secret Key: 56aU******************57cT
    Paco credentials file created at:

    /Users/bob/paco-project/.credentials.yaml

    It is NOT recommended to store this file in version control.
    Paco starter project include a .gitignore file to prevent this.
    You can store this file in a secrets mananger or re-create it again
    by generating a new AWS Api Key for the Paco Admin User and re-running
    this 'paco init credentials' command.


This will create a file named ``.credentials`` in your Paco project directory. Starting Paco projects also have a ``.gitignore``
file that will prevent you from committing this credentials file to a git repo. You can save this file somewhere secure,
or if it is lost use the AWS Console to create a new acccess key for your IAM User and re-run ``paco init credentials`` to
generate a new ``.credentials`` file.

Finally, use the ``paco validate`` command to verify your credentials allow you to connect to your AWS account.
The ``paco validate`` command generates CloudFormation templates and validates them in your AWS account.
Validate will never modify resources. It's a safe command to run to test the state of your Paco proejct.

.. code-block:: bash

    $ paco validate netenv.ne.prod


.. _Authy: https://authy.com/

.. _`Google Authenticator`: https://en.wikipedia.org/wiki/Google_Authenticator


