"""
All actions supported by CIS.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

from abc import ABC, abstractmethod
from func_timeout import func_timeout, FunctionTimedOut
import traceback


class Action(ABC):
    @staticmethod
    @abstractmethod
    def run(conv_list, params):
        """
        This is a static method for an abstract class. This method should run the corresponding action.

        Args:
            conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
            params(dict): A dict containing some mandatory and optional parameters.
        """
        pass


class RetrievalAction(Action):
    @staticmethod
    def run(conv_list, params):
        """
        The retrieval action runs the retrieval model and returns a list of documents.
        Args:
            conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
            params(dict): A dict containing some parameters. The parameter 'retrieval' is required, which should be the
            retrieval model object.

        Returns:
            A list of Documents.
        """
        return params['actions']['retrieval'].get_results(conv_list)


class GetDocFromIndex(Action):
    @staticmethod
    def run(conv_list, params):
        """
        Getting document from the collection index.
        Args:
            conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
            params(dict): A dict containing some parameters. The parameters 'retrieval' and 'doc_id' are required.

        Returns:
            A list of Documents with a length of 1.
        """
        return params['actions']['retrieval'].get_doc_from_index(params['doc_id'])


class QAAction(Action):
    @staticmethod
    def run(conv_list, params):
        """
        The question answering action runs the MRC model and returns a list of answers.
        Args:
            conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
            params(dict): A dict containing some parameters. The parameters 'qa' and 'doc' are required, which are the
            MRC model and the candidate document, respectively.

        Returns:
            A list of Documents containing the answers.
        """

        doc_list = RetrievalAction.run(conv_list, params)
        doc = ''
        for i in range(len(doc_list)):
            doc = doc_list[i].text
            if len(doc.strip()) > 0:
                break
        return params['actions']['qa'].get_results(conv_list, doc)


def run_action(action, conv_list, params, return_dict):
    """
    This method runs the specified action.

    Args:
        action(str): The action name, e.g., 'retrieval', 'qa', etc.
        conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
        user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
        params(dict): A dict containing some parameters.
        return_dict(dict): A shared dict for all processes running this action. The actions' outputs should be added to
        this dict.
    """
    if action == 'retrieval':
        action_func = RetrievalAction.run
    elif action == 'qa':
        action_func = QAAction.run
    else:
        raise Exception('Unknown Action!')

    try:
        return_dict[action] = func_timeout(params['timeout'], action_func, args=[conv_list, params])
    except FunctionTimedOut:
        params['logger'].warning('The action "%s" did not respond in %d seconds.', action, params['timeout'])
    except Exception:
        return_dict[action] = None
        traceback.print_exc()
