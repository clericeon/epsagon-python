"""
botocore events module
"""
from __future__ import absolute_import
from ..common import ErrorCode
from ..trace import tracer
from ..event import BaseEvent


class BotocoreEvent(BaseEvent):
    """
    Represents base botocore event
    """

    EVENT_MODULE = 'botocore'
    EVENT_TYPE = 'botocore'

    def __init__(self, instance, args):
        super(BotocoreEvent, self).__init__()

        event_operation, _ = args
        self.event_operation = str(event_operation)

        self.metadata = {
            'region': instance.meta.region_name,
        }

    def set_error(self, exception):
        tracer.error_code = ErrorCode.ERROR
        self.error_code = ErrorCode.ERROR
        self.metadata['error_message'] = str(exception['Message'])
        self.metadata['error_code'] = str(exception['Code'])

    def post_update(self, parsed_response):
        self.event_id = parsed_response['ResponseMetadata']['RequestId']
        self.metadata['retry_attempts'] = parsed_response['ResponseMetadata']['RetryAttempts']
        self.metadata['request_id'] = parsed_response['ResponseMetadata']['RequestId']
        self.metadata['status_code'] = parsed_response['ResponseMetadata']['HTTPStatusCode']

        if 'Error' in parsed_response:
            self.set_error({
                'Message': parsed_response['Error']['Message'],
                'Code': parsed_response['Error']['Code'],
            })


class BotocoreS3Event(BotocoreEvent):
    """
    Represents s3 botocore event
    """

    EVENT_TYPE = 's3'

    def __init__(self, instance, args):
        super(BotocoreS3Event, self).__init__(instance, args)
        _, request_data = args
        self.resource_name = request_data['Bucket']

    def post_update(self, parsed_response):
        super(BotocoreS3Event, self).post_update(parsed_response)

        # TODO: Need to extract bucket name from request
        # TODO: response data depends on request type
        #self.metadata['bucket'] = parsed_response['Name']
        #self.metadata['key'] = parsed_response['Contents'][0]['Key']


class BotocoreLambdaEvent(BotocoreEvent):
    """
    Represents lambda botocore event
    """

    EVENT_TYPE = 'lambda'

    def __init__(self, instance, args):
        super(BotocoreLambdaEvent, self).__init__(instance, args)
        _, request_data = args

        self.resource_name = request_data['FunctionName']
        self.metadata['payload'] = request_data['Payload']


class BotocoreEventFactory(object):

    FACTORY_DICT = {
        BotocoreS3Event.EVENT_TYPE: BotocoreS3Event,
        BotocoreLambdaEvent.EVENT_TYPE: BotocoreLambdaEvent,
    }

    @staticmethod
    def factory(instance, args):
        instance_type = getattr(instance, '_service_model').endpoint_prefix
        if instance_type not in BotocoreEventFactory.FACTORY_DICT:
            return BotocoreEvent(instance, args)

        return BotocoreEventFactory.FACTORY_DICT[instance_type](instance, args)