"""
The CIS class.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

from abc import ABC, abstractmethod
from func_timeout import func_timeout, FunctionTimedOut

from code import interface, util
from code.core.input_processing.user_requests_db import UserRequestsDB
from code.util.msg import Message


class CIS(ABC):
    def __init__(self, params):
        """
        A Conversational Information Seeking class containing some abstract methods. Each CIS application is expected to
        be inherited from this class.

        Args:
            params(dict): A dict containing some parameters.
        """
        self.params = params
        if params['mode'] == 'live':
            self.params['live_request_handler'] = self.live_request_handler
            self.msg_db = UserRequestsDB(host=self.params['user_requests_db_host'],
                                         port=self.params['user_requests_db_port'],
                                         dbname=self.params['user_requests_db_name'])
        elif params['mode'] == 'exp':
            self.params['experimental_request_handler'] = self.request_handler_func

        self.interface = interface.get_interface(params)
        self.nlp_util = util.NLPUtil(self.params)
        self.params['nlp_util'] = self.nlp_util
        self.timeout = self.params['timeout'] if 'timeout' in self.params else -1

    def live_request_handler(self, msg):
        try:
            # load conversation from the database and add the current message to the database
            conv = [msg] + self.msg_db.get_conv_history(user_id=msg.user_id, max_time=10 * 60 * 1000, max_count=10)
            self.msg_db.insert_one(msg)

            output_msg = func_timeout(self.timeout, self.request_handler_func, args=[conv])

            self.msg_db.insert_one(output_msg)
            return output_msg

        except FunctionTimedOut:
            msg_info = dict()
            msg_info['msg_id'] = msg.msg_info['msg_id']
            msg_info['msg_source'] = 'system'
            msg_info['msg_type'] = 'error'
            text = 'Time out, no result!'
            timestamp = util.current_time_in_milliseconds()
            error_msg = Message(msg.user_interface, msg.user_id, msg.user_info, msg_info, text, timestamp)
            self.msg_db.insert_one(error_msg)
            return error_msg

    # def experimental_request_handler(self, str_list):
    #     if not isinstance(str_list, list):
    #         raise Exception('The input should be a list!')
    #
    #     conv_list = []
    #     for i in range(len(str_list)):
    #         if not isinstance(str_list[i], str):
    #             raise Exception('Each element of the input should be a string!')
    #         user_info = {'first_name': 'NONE'}
    #         msg_info = {'msg_id': -1,
    #                     'msg_type': 'command' if str_list[i].startswith('#') else 'text',
    #                     'msg_source': 'user'}
    #         msg = Message(user_interface='NONE',
    #                       user_id=-1,
    #                       user_info=user_info,
    #                       msg_info=msg_info,
    #                       text=str_list[i],
    #                       timestamp=util.current_time_in_milliseconds())
    #         conv_list.append(msg)
    #     conv_list.reverse()
    #
    #     if self.timeout > 0:
    #         output_msg = func_timeout(self.timeout, self.request_handler_func, args=[conv_list])
    #     else:
    #         output_msg = self.request_handler_func(conv_list)
    #     return output_msg

    @abstractmethod
    def request_handler_func(self, conv_list):
        pass

    @abstractmethod
    def run(self):
        pass