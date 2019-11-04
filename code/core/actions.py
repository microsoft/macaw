from abc import ABC, abstractmethod


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
        return params['retrieval'].get_results(conv_list)


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
        return params['retrieval'].get_doc_from_index(params['doc_id'])


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
        return params['qa'].get_results(conv_list, params['doc'])