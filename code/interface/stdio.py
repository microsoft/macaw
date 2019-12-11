"""
The STDIO interface for interactive CIS.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

import time
import traceback

from code import util
from code.interface.interface import Interface
from code.core.interaction_handler.msg import Message


class StdioInterface(Interface):
    def __init__(self, params):
        super().__init__(params)
        self.msg_id = int(time.time())

    def run(self):
        while True:
            try:
                request = input('ENTER YOUR COMMAND: ').strip()
                if len(request) == 0:
                    continue
                user_info = {'first_name': 'STDIO',
                             'is_bot': 'False'
                             }
                msg_info = {'msg_id': self.msg_id,
                            'msg_type': 'command' if request.startswith('#') else 'text',
                            'msg_source': 'user'}
                self.msg_id += 1
                msg = Message(user_interface='stdio',
                              user_id=-1,
                              user_info=user_info,
                              msg_info=msg_info,
                              text=request,
                              timestamp=util.current_time_in_milliseconds())
                output = self.params['live_request_handler'](msg)
                self.result_presentation(output, {})
            except Exception as ex:
                traceback.print_exc()

    def result_presentation(self, response_msg, params):
        try:
            print('THE RESPONSE STARTS')
            print('----------------------------------------------------------------------')
            if response_msg.msg_info['msg_type'] == 'text':
                print(response_msg.text)
            elif response_msg.msg_info['msg_type'] == 'options':
                for (option_text, option_data, output_score) in response_msg.msg_info['options']:
                    print(option_data, ' | ', option_text)
            elif response_msg.msg_info['msg_type'] == 'error':
                print('ERROR: NO RESULT!')
            else:
                raise Exception('The msg_type is not recognized:', response_msg.msg_info['msg_type'])
            print('----------------------------------------------------------------------')
            print('THE RESPONSE STARTS')
        except Exception as ex:
            traceback.print_exc()

