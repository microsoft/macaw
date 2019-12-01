"""
The output post processing unit.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

from abc import ABC, abstractmethod

from code import util
from code.util.msg import Message


class OutputProcessing(ABC):
    @abstractmethod
    def __init__(self, params):
        self.params = params

    @abstractmethod
    def get_output(self, conv, candidate_outputs):
        pass


class NaiveOutputProcessing(OutputProcessing):
    def __init__(self, params):
        super().__init__(params)

    def get_output(self, conv, candidate_outputs):
        user_id = conv[0].user_id
        user_info = conv[0].user_info
        msg_info = dict()
        msg_info['msg_id'] = conv[0].msg_info['msg_id']
        msg_info['msg_source'] = 'system'
        text = ''
        user_interface = conv[0].user_interface

        if len(candidate_outputs) == 0:
            msg_info['msg_type'] = 'text'
            msg_info['msg_creator'] = 'no answer error'
            text = 'No response has been found! Please try again!'
        elif len(candidate_outputs) > 1:
            raise Exception('The output producer does not currently handle more than 1 candidate output!')
        else:
            if 'qa' in candidate_outputs:
                msg_info['msg_type'] = conv[0].msg_info['msg_type']
                msg_info['msg_creator'] = 'qa'
                text = candidate_outputs['qa'][0].text
            elif 'retrieval' in candidate_outputs:
                msg_info['msg_type'] = 'options'
                msg_info['msg_creator'] = 'retrieval'
                text = 'Retrieved document list (click to see the document content):'
                msg_info['options'] = [(output.title, '#get_doc ' + output.id, output.score) for output in candidate_outputs['retrieval']]
            elif '#get_doc' in candidate_outputs:
                msg_info['msg_type'] = 'text'
                msg_info['msg_creator'] = '#get_doc'
                text = candidate_outputs['#get_doc'][0].text
            else:
                raise Exception('The candidate output key is not familiar!')
        timestamp = util.current_time_in_milliseconds()
        if timestamp <= conv[0].timestamp:
            raise Exception('There is a problem in the output timestamp!')
        return Message(user_interface, user_id, user_info, msg_info, text, timestamp)
