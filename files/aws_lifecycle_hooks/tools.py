#!/usr/bin/env python
'''
File managed by puppet in module aws_lifecycle_hooks
'''
import json
import functools
import urllib.request
import urllib.error
import typing
import yaml
import attr

from exceptions import ParsingError


@attr.s
class VolumeAttachment:
    volume_id = attr.ib()
    device_name = attr.ib()


@functools.lru_cache(maxsize=1)
def get_instance_identity() -> typing.Mapping[str, typing.Any]:
    instance_identity = urllib.request.urlopen(
        "http://169.254.169.254/2016-09-02/dynamic/instance-identity/document"
    ).read()
    instance_identity = json.loads(instance_identity.decode('utf-8'))
    return instance_identity


def get_instance_id() -> str:
    instance_id = get_instance_identity()['instanceId']
    print("My instance_id is {instance_id}".format(instance_id=instance_id))
    return instance_id


def get_instance_region() -> str:
    instance_region = get_instance_identity()['region']
    print("My region is {instance_region}".format(instance_region=instance_region))
    return instance_region


@functools.lru_cache(maxsize=1)
def get_user_data() -> str:
    try:
        user_data = urllib.request.urlopen(
            "http://169.254.169.254/2016-09-02/user-data"
        ).read()
        print("My raw user-data is {user_data}".format(user_data=user_data))
        return user_data
    except urllib.error.HTTPError as e:
        if e.status == 404:
            print('No user_data found.')
        else:
            raise


@functools.lru_cache(maxsize=1)
def get_parsed_user_data() -> typing.Mapping[str, typing.Any]:
    user_data = get_user_data()
    if user_data:
        try:
            # every JSON file is also valid YAML, so we only need to parse YAML.
            user_data = yaml.safe_load(user_data)
            print("My parsed user-data is {user_data}".format(user_data=user_data))
        except yaml.YAMLError as e:
            raise ParsingError("Failed to parse User Data") from e

        return user_data


@functools.lru_cache()
def get_asg_name(
        instance_id: str,
        asg_client,
) -> str:
    asg_info = asg_client.describe_auto_scaling_instances(InstanceIds=[instance_id])
    asg_name = asg_info[u'AutoScalingInstances'][0][u'AutoScalingGroupName']
    print("I am part of Auto Scaling Group {asg_name}".format(asg_name=asg_name))

    return asg_name


def test_tools():
    import boto3

    instance_id = get_instance_id()
    region = get_instance_region()
    asg_client = boto3.client('autoscaling', region_name=region)
    """:type : pyboto3.autoscaling"""
    get_asg_name(instance_id, asg_client)
    get_user_data()
