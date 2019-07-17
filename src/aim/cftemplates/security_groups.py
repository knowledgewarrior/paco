import os
from aim.cftemplates.cftemplates import CFTemplate
from aim.cftemplates.cftemplates import Parameter
from aim.cftemplates.cftemplates import StackOutputParam
from io import StringIO
from enum import Enum


class SecurityGroups(CFTemplate):
    def __init__(self,
                 aim_ctx,
                 account_ctx,
                 aws_region,
                 subenv_ctx,
                 security_groups_config,
                 sg_group_id,
                 sg_group_config_ref):

        #aim_ctx.log("SecurityGroup CF Template init")

        self.subenv_ctx = subenv_ctx

        super().__init__(aim_ctx,
                         account_ctx,
                         aws_region,
                         config_ref=sg_group_config_ref,
                         aws_name='-'.join(["SecurityGroups", sg_group_id]))

        vpc_stack = self.subenv_ctx.get_vpc_stack()
        # Initialize Parameters
        self.set_parameter(StackOutputParam('VPC', vpc_stack, 'VPC'))

        # Define the Template
        template_header = """
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Security Groups'

Parameters:
  VPC:
    Description: 'VPC ID'
    Type: String

Resources:

"""
        sg_fmt = """
  {0[cf_sg_name]:s}:
    Type: 'AWS::EC2::SecurityGroup'
    Properties:
      GroupName: {0[group_name]:s}
      GroupDescription: {0[group_description]:s}
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: {0[group_name]:s}
"""

        sg_rule_fmt = """
  {0[cf_sg_rule_name]:s}:
    Type: AWS::EC2::SecurityGroup{0[cf_rule_type]:s}
    Properties:
      GroupId: !Ref {0[cf_sg_name]:s}
      IpProtocol: {0[protocol]:s}{0[from_port]:s}{0[to_port]:s}{0[source]:s}
"""

        sg_rule_output_fmt = """
  {0[cf_sg_name]:s}:
    Value: !Ref {0[cf_sg_name]:s}
"""

        template_yaml = template_header
        template_outputs = ""

        # Security Group and Ingress/Egress Resources
        for sg_name in sorted(security_groups_config.keys()):
            sg_config = security_groups_config[sg_name]
            sg_table = { 'cf_sg_name': '',
                         'group_name': '',
                         'group_description': '' }
            # Security Group
            sg_table['cf_sg_name'] = sg_name
            # Controller Name, Network Environment Name
            #sg_table['group_name'] = aim_ctx.config_controller.aws_name() + "-" + self.stack_group_ctx.aws_name + "-" + sg_name
            group_name = aim_ctx.normalized_join([self.subenv_ctx.netenv_id,
                                                  self.subenv_ctx.subenv_id,
                                                  sg_group_id,
                                                  sg_name],
                                                     '',
                                                     True)
            sg_table['group_name'] = group_name
            sg_table['group_description'] = "AIM generated Security Group"

            template_yaml += sg_fmt.format(sg_table)

            # Security Group Ingress and Egress rules
            for sg_rule_type in ['Ingress', 'Egress']:
                if sg_rule_type == 'Ingress':
                    sg_rule_list = sg_config.ingress
                elif sg_rule_type == 'Egress':
                    sg_rule_list = sg_config.egress
                else:
                    raise StackException(AimErrorCode.Unknown)
                    # Ingress and Egress rules have the same properties
                for sg_rule_config in sg_rule_list:
                    sg_rule_table = { 'cf_sg_rule_name': '',
                                      'cf_sg_name': '',
                                      'cf_rule_type': '',
                                      'protocol': '',
                                      'from_port': '',
                                      'to_port': '',
                                      'source': '' }

                    sg_rule_table['cf_sg_rule_name'] = sg_name + sg_rule_type + sg_rule_config.name
                    sg_rule_table['cf_sg_name'] = sg_table['cf_sg_name']
                    sg_rule_table['cf_rule_type'] = sg_rule_type
                    sg_rule_table['protocol'] = str(sg_rule_config.protocol)

                    # SourceSecurtiyGroupId or CidrIp are required
                    if sg_rule_config.cidr_ip != '':
                        sg_rule_table['source'] = '\n      CidrIp: ' + sg_rule_config.cidr_ip
                    elif sg_rule_config.source_security_group_id != '':
                        # XXX: TODO: This only handles references to security groups within the
                        #            template currently being generated.
                        local_ref = self.get_local_sg_ref(sg_rule_config.source_security_group_id)
                        sg_rule_table['source'] = '\n      SourceSecurityGroupId: !Ref ' + local_ref
                    else:
                        raise StackException(AimErrorCode.Unknown)

                    # Optional Properties
                    if sg_rule_config.from_port != '':
                        sg_rule_table['from_port'] = '\n      FromPort: ' + str(sg_rule_config.from_port)
                    if sg_rule_config.to_port != '':
                        sg_rule_table['to_port'] = '\n      ToPort: ' + str(sg_rule_config.to_port)

                    template_yaml += sg_rule_fmt.format(sg_rule_table)

            # Generate Outputs while we are in the loop
            template_outputs += sg_rule_output_fmt.format(sg_table)

        # Outputs Yaml
        template_yaml += """
Outputs:
"""
        template_yaml += template_outputs
        self.set_template(template_yaml)

    def validate(self):
        #self.aim_ctx.log("Validating SecurityGroups Template")
        super().validate()

    def get_local_sg_ref(self, aim_ref):
        ref_parts = aim_ref.split(' ')
        if ref_parts[0] != 'netenv.ref':
            raise StackException(AimErrorCode.Unknown)

        ref_parts = ref_parts[1].split('.')
        return ref_parts[-2]

    def get_outputs_key_from_ref(self, aim_ref):
        ref_dict = self.aim_ctx.aim_ref.parse_ref(aim_ref)
        ref_parts = ref_dict['ref_parts']
        network_component = ref_parts[5]
        vpc_component = ref_parts[6]
        sg_component = ref_parts[7]
        sg_id = ref_parts[8]

        if ref_dict['subenv_component'] != 'subenv':
            raise StackException(AimErrorCode.Unknown)
        if ref_dict['netenv_component'] != 'network':
            raise StackException(AimErrorCode.Unknown)
        if network_component != 'vpc':
            raise StackException(AimErrorCode.Unknown)
        if vpc_component != 'security_groups':
            raise StackException(AimErrorCode.Unknown)

        # Output key is the specific security group id in the yaml config
        return sg_id
