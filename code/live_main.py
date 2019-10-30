from code.cis import CIS
from code.core import mrc, retrieval
from code.core.input_processing.action_detection import RequestDispatcher
from code.core.output_processing.output_selection import output_processing
from code.util.logging import Logger

class ConvQA(CIS):
    def __init__(self, params):
        super().__init__(params)
        self.logger = params['logger']
        self.logger.info('Conversational QA Model... starting up...')
        self.retrieval = retrieval.get_retrieval_model(params=self.params)
        self.qa = mrc.get_mrc_model(params=self.params)
        self.request_dispatcher = RequestDispatcher({'retrieval': self.retrieval,
                                                     'qa': self.qa})
        self.output_selection = output_processing.NaiveOutputProcessing({})

    def request_handler_func(self, conv_list):
        # identify action
        print(conv_list)
        dispatcher_output = self.request_dispatcher.dispatch(conv_list)
        output_msg = self.output_selection.get_output(conv_list, dispatcher_output)
        return output_msg

    def run(self):
        self.interface.run()


if __name__ == '__main__':
    basic_params = {'timeout': 15,  # timeout is in terms of second.
                    'mode': 'live',  # mode can be either live or exp.
                    'logger': Logger({})}  # for logging into file, pass the filepath to the Logger class.
    db_params = {'user_requests_db_host': 'localhost',
                 'user_requests_db_port': 27017,
                 'user_requests_db_name': 'macaw_test'}
    interface_params = {'interface': 'telegram',
                        'bot_token': '920831379:AAFt_jr7bK4sFuv4FJ1hWIWqABoEa9w9708',
                        'asr_model': 'google',
                        'asg_model': 'google',
                        'google-speech-to-text-credential-file': '/mnt/e/projects/macaw/data/macaw-a9446332dcc5.json'}
    retrieval_params = {'query_generation': 'simple',
                        'search_engine': 'indri',
                        'bing_key': '7a9b8a186d414184abecb3ac6ef7d296',  # only for Bing Web Search
                        'search_engine_path': '/mnt/e/indri-5.11/',
                        'col_index': '/mnt/e/indri-index/robust_indri/indri_index',
                        'col_text_format': 'trectext',
                        'results_requested': 3}
    mrc_params = {'mrc': 'drqa',
                  'mrc_model_path': '/mnt/e/test/DrQA/data/reader/multitask.mdl',
                  'mrc_path': '/mnt/e/test/DrQA/',
                  'corenlp_path': '/mnt/e/test/DrQA/data/corenlp/',
                  'qa_results_requested': 3}

    params = {**basic_params, **db_params, **interface_params, **retrieval_params, **mrc_params}
    basic_params['logger'].info(params)
    ConvQA(params).run()
