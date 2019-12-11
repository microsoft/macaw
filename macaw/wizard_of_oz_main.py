"""
The interactive CIS main file.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

import multiprocessing

from macaw import interface
from macaw.core import retrieval
from macaw.core.input_handler.action_detection import RequestDispatcher
from macaw.core.interaction_handler.user_requests_db import InteractionDB
from macaw.core.output_handler import naive_output_selection
from macaw.util.logging import Logger


class Seeker:
    def __init__(self, params):
        """
        The constructor for Conversational Question Answering. This is a Conversational application class and is
        inherited from the CIS class.

        Args:
            params(dict): A dict of parameters. These are mandatory parameters for this class: 'logger' which is an
            instance of the util.logging.Logger class. ConvQA requires both a retrieval and machine reading
            comprehension engines. Each of them requires some additional parameters. Refer to the corresponding class
            for more information on the required parameters.
        """
        self.params = params
        self.logger = params['logger']
        self.logger.info('Conversational Wirzard of Oz System... starting up...')
        self.wizard = None
        self.params['live_request_handler'] = self.live_request_handler

        self.interface = interface.get_interface(params)

        self.retrieval = retrieval.get_retrieval_model(params=self.params)
        self.request_dispatcher = RequestDispatcher({'retrieval': self.retrieval})
        self.output_selection = naive_output_selection.NaiveOutputProcessing({})

    def live_request_handler(self, msg):
        """
        This function is called for each conversational interaction made by the user. In fact, this function calls the
        dispatcher to send the user request to the information seeking components.

        Args:
            conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.

        Returns:
            output_msg(Message): Returns an output message that should be sent to the UI to be presented to the user.
        """
        msg_db = InteractionDB(host=self.params['user_requests_db_host'],
                               port=self.params['user_requests_db_port'],
                               dbname=self.params['user_requests_db_name'])
        msg_db.insert_one(msg)
        msg_db.close()
        self.logger.info(msg)
        # dispatcher_output = self.request_dispatcher.dispatch(conv_list)
        # output_msg = self.output_selection.get_output(conv_list, dispatcher_output)

        self.wizard.send_msg(msg.text)

    def set_wizard(self, wizard):
        self.wizard = wizard

    def send_msg(self, msg_text):
        self.interface.send_msg(self.params['user_id'], msg_text)

    def run(self):
        """
            This function is called to run the ConvQA system. In live mode, it never stops until the program is killed.
        """
        self.interface.run()


class Wizard:
    def __init__(self, params):
        """
        The constructor for Conversational Question Answering. This is a Conversational application class and is
        inherited from the CIS class.

        Args:
            params(dict): A dict of parameters. These are mandatory parameters for this class: 'logger' which is an
            instance of the util.logging.Logger class. ConvQA requires both a retrieval and machine reading
            comprehension engines. Each of them requires some additional parameters. Refer to the corresponding class
            for more information on the required parameters.
        """
        self.params = params
        self.logger = params['logger']
        self.logger.info('Conversational Wirzard of Oz System... starting up...')
        self.params['live_request_handler'] = self.live_request_handler
        self.seeker = None

        self.interface = interface.get_interface(params)

        self.retrieval = retrieval.get_retrieval_model(params=self.params)
        self.request_dispatcher = RequestDispatcher({'retrieval': self.retrieval})
        self.output_selection = naive_output_selection.NaiveOutputProcessing({})

    def live_request_handler(self, msg):
        """
        This function is called for each conversational interaction made by the user. In fact, this function calls the
        dispatcher to send the user request to the information seeking components.

        Args:
            conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.

        Returns:
            output_msg(Message): Returns an output message that should be sent to the UI to be presented to the user.
        """
        msg_db = InteractionDB(host=self.params['interaction_db_host'],
                               port=self.params['interaction_db_port'],
                               dbname=self.params['interaction_db_name'])
        msg_db.insert_one(msg)
        self.logger.info(msg)

        if msg.text.startswith('@seeker'):
            self.seeker.send_msg(msg.text[7:].strip())
            output_msg = None
        elif msg.text.startswith('@system'):
            msg.text = msg.text[7:].strip()
            dispatcher_output = self.request_dispatcher.dispatch([msg])
            output_msg = self.output_selection.get_output([msg], dispatcher_output)
            msg_db.insert_one(output_msg)
        elif msg.text.startswith('@logger'):
            msg_db.close()
            output_msg = None
        else:
            self.send_msg('The message should starts with @system, @seeker, or @logger')
            output_msg = None

        msg_db.close()
        return output_msg

    def set_seeker(self, seeker):
        self.seeker = seeker

    def send_msg(self, msg_text):
        self.interface.send_msg(self.params['user_id'], msg_text)

    def run(self):
        """
            This function is called to run the ConvQA system. In live mode, it never stops until the program is killed.
        """
        self.interface.run()


if __name__ == '__main__':
    basic_params = {'timeout': 15,  # timeout is in terms of second.
                    'mode': 'live',  # mode can be either live or exp.
                    'logger': Logger({})}  # for logging into file, pass the filepath to the Logger class.

    # These are required database parameters if the mode is 'live'. The host and port of the machine hosting the
    # database, as well as the database name.
    db_params = {'user_requests_db_host': 'localhost',
                 'user_requests_db_port': 27017,
                 'user_requests_db_name': 'macaw_test'}

    # These are interface parameters. They are interface specific.
    seeker_interface_params = {'interface': 'telegram',  # interface can be 'telegram' or 'stdio'.
                               'bot_token': '920831379:AAFt_jr7bK4sFuv4FJ1hWIWqABoEa9w9708',  # Telegram bot token.
                               'asr_model': 'google',  # The API used for speech recognition.
                               'asg_model': 'google',  # The API used for speech generation.
                               'google-speech-to-text-credential-file': '/mnt/e/projects/macaw/data/macaw-a9446332dcc5.json',
                               'user_id': '127075246'}

    wizard_interface_params = {'interface': 'telegram',  # interface can be 'telegram' or 'stdio'.
                               'bot_token': '832589037:AAFxAEYTJwsQsMph6Ob6FF9VF71MP57mWK4',  # Telegram bot token.
                               'asr_model': 'google',  # The API used for speech recognition.
                               'asg_model': 'google',  # The API used for speech generation.
                               'google-speech-to-text-credential-file': '/mnt/e/projects/macaw/data/macaw-a9446332dcc5.json',
                               'user_id': '127075246'}

    # These are parameters used by the retrieval model.
    retrieval_params = {'query_generation': 'simple',  # the model that generates a query from a conversation history.
                        'use_coref': False,  # True, if query generator can use coreference resolution, otherwise False.
                        'search_engine': 'indri',  # the search engine. It can be either 'indri' or 'bing'.
                        'bing_key': '7a9b8a186d414184abecb3ac6ef7d296',  # Bing API key
                        'search_engine_path': '/mnt/e/indri-5.11/',  # The path to the indri toolkit.
                        'col_index': '/mnt/e/indri-index/robust_indri/indri_index',  # The path to the indri index.
                        'col_text_format': 'trectext',  # collection text format. Standard 'trectext' is only supported.
                        'results_requested': 3}  # Maximum number of docs that should be retrieved by search engine.
    # Note: If you want to have a re-ranking model (e.g., learning to rank), you just need to simply extend the class
    # core.retrieval.search_engine.ReRanker and implement the method 'rerank'. Then simply add a 'reranker' parameter to
    # retrieval_params that points to an instance of your favorite ReRanker class. If there is a 'reranker' parameter in
    # retrieval_params, the retrieval model automatically calls the re-ranking method. For more details, see the method
    # 'get_results' in class core.retrieval.search_engine.Retrieval.

    seeker_params = {**basic_params, **db_params, **seeker_interface_params, **retrieval_params}
    wizard_params = {**basic_params, **db_params, **wizard_interface_params, **retrieval_params}
    basic_params['logger'].info(seeker_params)
    basic_params['logger'].info(wizard_params)

    seeker = Seeker(seeker_params)
    wizard = Wizard(wizard_params)
    seeker.set_wizard(wizard)
    wizard.set_seeker(seeker)

    seeker_process = multiprocessing.Process(target=seeker.run)
    wizard_process = multiprocessing.Process(target=wizard.run)

    seeker_process.start()
    wizard_process.start()

    basic_params['logger'].info('Seeker Process ID: {}'.format(seeker_process.pid))
    basic_params['logger'].info('Wizard Process ID: {}'.format(wizard_process.pid))

