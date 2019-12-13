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
        q = conv_list[0].text
        if 'use_coref' in self.params and self.params['use_coref']:
            q_coref = self.get_query_coref(conv_list)
            for key in q_coref:
                q += ' ' + ' '.join(q_coref[key])

        q = q.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation))).strip()

        # print(q)
        return q

    def get_query_coref(self, conv_list):
        """
        This methods compute all co-references in the conversation history for the query terms (i.e., those in the last
        interaction).

        Args:
            conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.

        Returns:
            A dict from terms in the last user request to a list of all identified co-references.

        """
        corenlp_coref_result = self.compute_corefs(conv_list)
        q_coref = dict()
        last_index = len(corenlp_coref_result['sentences'])
        for key in corenlp_coref_result['corefs']:
            has_coref = False
            for item in corenlp_coref_result['corefs'][key]:
                if item['sentNum'] == last_index:
                    has_coref = True
                    text = item['text']
                    break
            if has_coref:
                q_coref[text] = []
                for item in corenlp_coref_result['corefs'][key]:
                    if item['sentNum'] == last_index:
                        continue
                    q_coref[text].append(item['text'])
        return q_coref

    def compute_corefs(self, conv_list):
        """
        This method runs CoreNLP co-reference resolution on the requests made by the user in the conversation.
        Note: this method ignores system responses.

        Args:
            conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.

        Returns:
            A dict containing all sentence and co-reference information.

        """
        conv_history = []
        for msg in reversed(conv_list):
            if msg.msg_info['msg_source'] == 'user' and msg.msg_info['msg_type'] in ['text', 'voice']:
                temp = msg.text if msg.text.endswith('?') else (msg.text + '?')
                conv_history.append(temp)
            # elif msg.msg_info['msg_source'] == 'system' and msg.msg_info['msg_type'] == 'text' and len(msg.text.split()) < 30:
            #     temp = msg.text + '.'
            #     conv_history.append(temp)
        if len(conv_history) == 0:
            raise Exception('The query generation model cannot generate any query! There should be a problem')
        coref_results = self.params['nlp_util'].get_coref(' '.join(conv_history))
        return coref_results


