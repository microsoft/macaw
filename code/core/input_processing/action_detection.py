"""
The request dispatcher module.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

import copy
import multiprocessing

from code.core import actions


class PreActionRequestDispatcher:
    def __init__(self, params):
        self.params = params

    def action_detection(self, conv_list):
        if conv_list[0].msg_info['msg_type'] == 'command':
            command = conv_list[0].text.split(' ')[0]
            return command

        if 'qa' in self.params:
            if conv_list[0].text.endswith('?') \
                    or conv_list[0].text.lower().startswith('what') \
                    or conv_list[0].text.lower().startswith('who') \
                    or conv_list[0].text.lower().startswith('when') \
                    or conv_list[0].text.lower().startswith('where') \
                    or conv_list[0].text.lower().startswith('how') \
                    or conv_list[0].text.lower().startswith('is') \
                    or conv_list[0].text.lower().startswith('are'):
                return 'qa'
        if 'retrieval' in self.params:
            return 'retrieval'

    def dispatch(self, conv_list):
        action = self.action_detection(conv_list)
        if action == 'retrieval':
            return {'retrieval': actions.RetrievalAction.run(conv_list, self.params)}
        if action == 'qa':
            return {'qa': actions.QAAction.run(conv_list, self.params)}
        if action == '#get_doc':
            doc_id = ' '.join(conv_list[0].text.split(' ')[1:])
            return {'#get_doc': actions.GetDocFromIndex.run(None, {**self.params, **{'doc_id': doc_id}})}


class RequestDispatcher:
    def __init__(self, params):
        self.params = params

    def dispatch(self, conv_list):
        if conv_list[0].msg_info['msg_type'] == 'command':
            command = conv_list[0].text.split(' ')[0]
            return self.execute_command(conv_list, command)

        params = {'actions': self.params['actions'], 'timeout': self.params['timeout']}
        action_processes = []
        manager = multiprocessing.Manager()
        action_results = manager.dict()
        for action in self.params['actions']:
            p = multiprocessing.Process(target=actions.run_action, args=[action, conv_list.copy(), params, action_results])
            action_processes.append(p)
            p.start()

        for p in action_processes:
            p.join()

        candidate_outputs = dict()
        for key in action_results:
            if action_results[key]:
                candidate_outputs[key] = action_results[key]
        return candidate_outputs

    def execute_command(self, conv_list, command):
        if command == '#get_doc':
            doc_id = ' '.join(conv_list[0].text.split(' ')[1:])
            return {'#get_doc': actions.GetDocFromIndex.run(None, {**self.params, **{'doc_id': doc_id}})}
        else:
            raise Exception('Command not found!')
