from abc import ABC, abstractmethod
import string

class QueryGeneration(ABC):
    @abstractmethod
    def __init__(self, params):
        self.params = params

    @abstractmethod
    def get_query(self, conv_list):
        pass


class SimpleQueryGeneration(QueryGeneration):
    def __init__(self, params):
        super().__init__(params)

    def get_query(self, conv_list):
        # q = ' '.join(msg.text for msg in conv_list)
        print(self.compute_corefs(conv_list))
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
        print('############ ', ' '.join(conv_history))
        return coref_results
