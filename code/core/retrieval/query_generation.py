"""
The query generation model for search engine.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

from abc import ABC, abstractmethod
import string

class QueryGeneration(ABC):
    @abstractmethod
    def __init__(self, params):
        """
        An abstract class for query generation models.

        Args:
            params(dict): A dict containing some mandatory and optional parameters.
        """
        self.params = params

    @abstractmethod
    def get_query(self, conv_list):
        """
        This method is called to get the query generated from a list of conversational interactions.

        Args:
            conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.

        Returns:
            The inherited class should implements this method and return a str containing a query for retrieval purpose.
        """
        pass


class SimpleQueryGeneration(QueryGeneration):
    def __init__(self, params):
        """
        This class is a simple implementation of query generation that only focuses on the last interaction in the
        conversation and use the last interaction as the query.

        Args:
            params(dict): A dict containing some mandatory and optional parameters.
        """
        super().__init__(params)

    def get_query(self, conv_list):
        """
        This method generates a query from a list of conversational interactions by using the last user request, with
        some pre-processing (e.g., removing punctuations).

        Args:
            conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.

        Returns:
            A str containing the query for retrieval.
        """
        # q = ' '.join(msg.text for msg in conv_list)
        # print(self.compute_corefs(conv_list))
        q = conv_list[0].text
        q = q.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation))).strip()
        return q

    def compute_corefs(self, conv_list):
        conv_history = []
        for msg in reversed(conv_list):
            if msg.msg_info['msg_source'] == 'user' and msg.msg_info['msg_type'] == 'text':
                temp = msg.text if msg.text.endswith('?') else (msg.text + '?')
                conv_history.append(temp)
            # elif msg.msg_info['msg_source'] == 'system' and msg.msg_info['msg_type'] == 'text' and len(msg.text.split()) < 30:
            #     temp = msg.text + '.'
            #     conv_history.append(temp)
        if len(conv_history) == 0:
            raise Exception('The query generation model cannot generate any query! There should be a problem')
        coref_results = self.params['nlp_util'].get_coref(' '.join(conv_history))
        # print('############ ', ' '.join(conv_history))
        return coref_results
