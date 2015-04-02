# beanstalk.py
#!/usr/bin/python

from troposphere import (
    GetAtt, Join, Output,
    Parameter, Ref, Template, FindInMap
)

from troposphere.elasticbeanstalk import (
    Application, ApplicationVersion, ConfigurationTemplate, Environment,
    SourceBundle, OptionSettings
)

from troposphere.iam import Role, InstanceProfile
from troposphere.iam import PolicyType as IAMPolicy

t = Template()

env=t.add_parameter(Parameter(
	"env",
	Description="Name of the Beanstalk environment",
	Type="String",
	Default="local"))

keyname=t.add_parameter(Parameter(
	"KeyName",
	Description="Name of the ec2 ssh keypair name",
	Type="AWS::EC2::KeyPair::KeyName"))

t.add_resource(Application(
	"user",
	Description="AWS Beanstalk stack for user module"))

t.add_resource(ApplicationVersion(
    "userAppVersion",
    Description="Version 1.0",
    ApplicationName=Ref("user"),
    SourceBundle=SourceBundle(
        S3Bucket=Join("-", ["elasticbeanstalk-samples", Ref("AWS::Region")]),
        S3Key="nodejs-sample.zip"
    )
))

t.add_resource(ConfigurationTemplate(
    "userConfigurationTemplate",
    ApplicationName=Ref("user"),
    Description="User module Tomcat 7 with Java 7",
    SolutionStackName="64bit Amazon Linux 2014.09 v1.2.0 running Tomcat 7 Java 7",
    OptionSettings=[
        OptionSettings(
            Namespace="aws:autoscaling:launchconfiguration",
            OptionName="EC2KeyName",
            Value=Ref("KeyName")
        )
    ]
))

t.add_resource(Environment(
    "userBeanstalkEnv",
    Description="AWS Elastic Beanstalk Environment for user module",
    ApplicationName=Ref("user"),
    EnvironmentName=Ref("env"),
    TemplateName=Ref("userConfigurationTemplate"),
    VersionLabel=Ref("userAppVersion")
))

print t.to_json()