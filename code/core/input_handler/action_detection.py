"""
The request dispatcher module.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

import multiprocessing

from code.core.input_handler import actions


class PreActionRequestDispatcher:
    def __init__(self, params):
        """
        A simple pre-action request dispatcher module that selects one of the actions based on the user's message and
        only run one action.

        Args:
            params(dict): A dict of parameters.
        """
        self.params = params

    def action_detection(self, conv_list):
        """
        Action detection based on the conversation. This method simply identifies if a message is a command or if it's a
        question based on the starting word.

        Args:
            conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.

        Returns:
            A str denoting the identified action, e.g., 'retrieval', 'qa', or a command.

        """
        if conv_list[0].msg_info['msg_type'] == 'command':
            command = conv_list[0].text.split(' ')[0]
            return command

        if 'qa' in self.params:
            if conv_list[0].text.lower().startswith('what') \
                    or conv_list[0].text.lower().startswith('who') \
                    or conv_list[0].text.lower().startswith('when') \
                    or conv_list[0].text.lower().startswith('where') \
                    or conv_list[0].text.lower().startswith('how'):
                return 'qa'
        if 'retrieval' in self.params:
            return 'retrieval'

    def dispatch(self, conv_list):
        """
        A dispatcher function that runs the action identified by 'action_detection'.

        Args:
            conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.

        Returns:
            A dict of str (i.e., action) to list of Documents (i.e., the action's result) as the response.

        """
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
        """
        The main request dispatcher class. This module runs multiple actions in parallel for a pre-specified timeout and
        returns all of the obtained results.

        Args:
            params(dict): A dict of parameters. Required params include 'actions' and 'timeout'.
        """
        self.params = params

    def dispatch(self, conv_list):
        """
        The request dispatcher method. This method runs all non-command messages in parallel using multiprocessing.

        Args:
            conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.

        Returns:
            A dict of str (i.e., action) to list of Documents (i.e., the action's result) as the response.
        """
        if conv_list[0].msg_info['msg_type'] == 'command':
            command = conv_list[0].text.split(' ')[0]
            return self.execute_command(conv_list, command)

        params = {'actions': self.params['actions'],
                  'timeout': self.params['timeout'],
                  'logger': self.params['logger']}
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
        """
        The command executor method.

        Args:
            conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
            command(str): A str showing the command.

        Returns:
            A dict of str (i.e., command) to list of Documents (i.e., the action's result) as the response.
        """
        if command == '#get_doc':
            doc_id = ' '.join(conv_list[0].text.split(' ')[1:])
            return {'#get_doc': actions.GetDocFromIndex.run(None, {**self.params, **{'doc_id': doc_id}})}
        else:
            raise Exception('Command not found!')
