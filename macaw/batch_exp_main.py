"""
The main file for an experimental CIS with batch interaction support.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

from macaw.cis import CIS
from macaw.core import mrc, retrieval
from macaw.core.response.action_detection import RequestDispatcher
from macaw.core.output_handler import naive_output_selection


class ConvSearch(CIS):
    def __init__(self, params):
        super().__init__(params)
        self.retrieval = retrieval.get_retrieval_model(params=self.params)
        self.qa = mrc.get_mrc_model(params=self.params)
        self.request_dispatcher = RequestDispatcher({'retrieval': self.retrieval, 'qa': self.qa})
        self.output_selection = naive_output_selection.NaiveOutputProcessing({})

    def request_handler_func(self, conv_list):
        # identify action
        dispatcher_output = self.request_dispatcher.dispatch(conv_list)

        output_msg = self.output_selection.get_output(conv_list, dispatcher_output)
        return output_msg

    def run(self):
        self.interface.run()


if __name__ == '__main__':
    basic_params = {'timeout': -1,  # timeout is in terms of second.
                    'mode': 'exp'}  # mode can be either live or exp.
    interface_params = {'interface': 'fileio',
                        'input_file_path': 'INPUT_FILE',
                        'output_file_path': 'OUTPUT_FILE',
                        'output_format': 'text'}
    retrieval_params = {'query_generation': 'simple',
                        'search_engine': 'bing',  # 'bing' or 'indri'
                        'use_coref': True,  # True, if query generator can use coreference resolution, otherwise False.
                        'bing_key': 'YOUR_BING_SUBSCRIPTION_TOKEN',  # only for Bing Web Search
                        'search_engine_path': 'PATH_TO_INDRI',  # only for Indri
                        'col_index': 'PATH_TO_INDRI_INDEX',  # only for Indri
                        'col_text_format': 'trectext',  # trectext or trecweb. Only for Indri.
                        'results_requested': 3}
    mrc_params = {'mrc': 'drqa',
                  'mrc_model_path': 'PATH_TO_PRETRAINED_MRC_MODEL',
                  'mrc_path': 'PATH_TO_MRC_DIRECTORY',
                  'corenlp_path': 'PATH_TO_STANFORD_CORE_NLP_DIRECTORY',
                  'qa_results_requested': 3}

    params = {**basic_params, **interface_params, **retrieval_params, **mrc_params}
    ConvSearch(params).run()