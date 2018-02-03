"""
Runner for AWS Lambda
"""

from __future__ import absolute_import
import os
import time
from ..event import BaseEvent
from ..trace import tracer
from ..common import ErrorCode
from .. import constants


class LambdaRunner(BaseEvent):
    """
    Represents Lambda event runner
    """

    ORIGIN = 'runner'
    RESOURCE_TYPE = 'lambda'
    OPERATION = 'invoke'

    def __init__(self, context):
        """
        Initialize.
        :param context: Lambda's context (passed from entry point)
        """

        super(LambdaRunner, self).__init__(time.time())

        self.event_id = context.aws_request_id
        self.resource['name'] = context.function_name
        self.resource['operation'] = self.OPERATION
        self.resource['metadata'] = {
            'log_stream_name': context.log_stream_name,
            'log_group_name': context.log_group_name,
            'function_version': context.function_version,
            'memory': context.memory_limit_in_mb,
            'cold_start': constants.COLD_START,
            'region': os.environ.get('AWS_REGION', ''),
        }

    def set_exception(self, exception, traceback):
        """
        Sets exception data on event.
        :param exception: Exception object
        :param traceback: traceback string
        :return: None
        """
        tracer.error_code = ErrorCode.EXCEPTION
        self.error_code = ErrorCode.EXCEPTION
        self.resource['metadata']['exception'] = repr(exception)
        self.resource['metadata']['traceback'] = traceback
