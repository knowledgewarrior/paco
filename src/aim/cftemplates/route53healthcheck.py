"""
CloudFormation template for a Route53 health check
"""
import troposphere
import troposphere.route53
import troposphere.cloudwatch
from aim.cftemplates.cw_alarms import CFBaseAlarm
from aim.models import references
from aim.models.locations import get_parent_by_interface
from aim.models.metrics import CloudWatchAlarm


class Route53HealthCheck(CFBaseAlarm):
    """
    CloudFormation template for a Route53 health check
    """
    def __init__(
        self,
        aim_ctx,
        account_ctx,
        aws_region,
        stack_group,
        stack_tags,
        resource,
    ):
        # Route53 metrics only go to us-east-1
        # save the app region so it can be used in Name and Tags
        self.app_aws_region = aws_region
        aws_region = 'us-east-1'
        self.health_check = resource
        self.alarm_action_param_map = {}
        self.notification_param_map = {}
        super().__init__(
            aim_ctx,
            account_ctx,
            aws_region,
            config_ref=self.health_check.aim_ref_parts,
            stack_group=stack_group,
            stack_tags=stack_tags,
            enabled=self.health_check.is_enabled(),
        )
        self.set_aws_name('Route53HealthCheck', self.health_check.name)

        # Troposphere Template Initialization
        self.init_template('Route 53 health check')

        # Health check Resource
        health_check_logical_id = self.create_cfn_logical_id('Route53HealthCheck' + self.health_check.name)
        cfn_export_dict = {}
        cfn_export_dict['HealthCheckConfig'] = self.health_check.cfn_export_dict
        fqdn_param = self.create_cfn_parameter(
            param_type = 'String',
            name = 'FQDNEndpoint',
            description = 'Fully-qualified domain name of the endpoint to monitor.',
            value = self.health_check.load_balancer + '.dnsname',
            use_troposphere = True
        )
        self.template.add_parameter(fqdn_param)
        cfn_export_dict['HealthCheckConfig']['FullyQualifiedDomainName'] = troposphere.Ref(fqdn_param)
        # Set the Name in the HealthCheckTags
        # Route53 is global, but we add the app's region in the name
        cfn_export_dict['HealthCheckTags'] = troposphere.Tags(Name=self.aws_name + '-' + self.app_aws_region)

        health_check_resource = troposphere.route53.HealthCheck.from_dict(
            health_check_logical_id,
            cfn_export_dict
        )
        self.template.add_resource(health_check_resource)

        # CloudWatch Alarm
        # ToDo: allow configurtion of this alarm from the model
        alarm = CloudWatchAlarm('HealthCheckAlarm', self.health_check)
        alarm.overrode_region_name = 'us-east-1'
        alarm.metric_name = "HealthCheckPercentageHealthy"
        alarm.classification = 'health'
        alarm.severity = 'critical'
        alarm.namespace = "AWS/Route53"
        alarm.period = 60
        alarm.evaluation_periods = 1
        alarm.threshold = 18.0 # As recommended by AWS
        alarm.comparison_operator = 'LessThanOrEqualToThreshold'
        alarm.statistic = "Minimum"
        alarm.treat_missing_data = 'breaching'
        cfn_export_dict = alarm.cfn_export_dict
        cfn_export_dict['Dimensions'] = [{
            'Name': 'HealthCheckId',
            'Value': troposphere.Ref(health_check_resource),
        }]
        notification_cfn_refs = self.create_notification_params(alarm)
        cfn_export_dict['AlarmDescription'] = alarm.get_alarm_description(notification_cfn_refs)
        self.set_alarm_actions_to_cfn_export(alarm, cfn_export_dict)
        alarm_resource = troposphere.cloudwatch.Alarm.from_dict(
            'HealthCheckAlarm',
            cfn_export_dict
        )
        alarm_resource.DependsOn = health_check_logical_id
        self.template.add_resource(alarm_resource)

        # Generate the Template
        self.set_template(self.template.to_yaml())
