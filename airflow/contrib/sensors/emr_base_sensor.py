# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from airflow.operators.sensors import BaseSensorOperator
from airflow.utils import apply_defaults
from airflow.exceptions import AirflowException


class EmrBaseSensor(BaseSensorOperator):
    """
    Contains general sensor behavior for EMR.
    Subclasses should implement get_emr_response() and state_from_response() methods.
    Subclasses should also implment NON_TERMINAL_STATES and FAILED_STATE constants.
    """

    @apply_defaults
    def __init__(
            self,
            aws_conn_id='aws_default',
            *args, **kwargs):
        super(EmrBaseSensor, self).__init__(*args, **kwargs)
        self.aws_conn_id = aws_conn_id

    def poke(self, context):
        response = self.get_emr_response()

        if not response['ResponseMetadata']['HTTPStatusCode'] == 200:
            logging.info('Bad HTTP response: %s' % response)
            return False

        state = self.state_from_response(response)
        logging.info('Job flow currently %s' % state)

        if state in self.NON_TERMINAL_STATES:
            return False

        if state == self.FAILED_STATE:
            raise AirflowException('EMR job failed')

        return True
