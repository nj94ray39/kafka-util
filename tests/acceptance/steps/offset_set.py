import os

from behave import then
from behave import when
from util import call_cmd
from util import get_cluster_config

from yelp_kafka_tool.util.zookeeper import ZK


SET_OFFSET = 36
SET_OFFSET_KAFKA = 65


def offsets_data(topic, offset):
    return '''{topic}.{partition}={offset}'''.format(
        topic=topic,
        partition='0',
        offset=offset,
    )


def call_offset_set(groupid, offsets_data, storage=None, force=None):
    cmd = ['kafka-consumer-manager',
           '--cluster-type', 'test',
           '--cluster-name', 'test_cluster',
           '--discovery-base-path', 'tests/acceptance/config',
           'offset_set',
           groupid,
           offsets_data]
    if storage:
        cmd.extend(['--storage', storage])
    if force:
        cmd.extend(['--force', force])
    return call_cmd(cmd)


@when(u'we call the offset_set command with a groupid and offset data')
def step_impl2(context):
    context.offsets = offsets_data(context.topic, SET_OFFSET)
    call_offset_set(context.group, context.offsets)


@when(u'we call the offset_set command and commit into kafka')
def step_impl2_2(context):
    if '0.9.0' == os.environ['KAFKA_VERSION']:
        if not hasattr(context, 'group'):
            context.group = 'test_kafka_offset_group'
        context.offsets = offsets_data(context.topic, SET_OFFSET_KAFKA)
        call_offset_set(context.group, context.offsets, storage='kafka')


@when(u'we call the offset_set command with a new groupid and the force option')
def step_impl2_3(context):
    context.offsets = offsets_data(context.topic, SET_OFFSET)
    context.group = 'offset_set_created_group'
    call_offset_set(context.group, context.offsets, force='force')


@then(u'the committed offsets will match the specified offsets')
def step_impl3(context):
    cluster_config = get_cluster_config()
    with ZK(cluster_config) as zk:
        offsets = zk.get_group_offsets(context.group)
    assert offsets[context.topic]["0"] == SET_OFFSET
