"""
The interactive CIS main file.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""
import argparse
from typing import List

from core.interaction_handler import Message
from core.response.punctuation import ResponseGeneratorPunctuation
from macaw.cis import CIS
from macaw.core import mrc, retrieval
from macaw.util.custom_logging import LoggerFactory


class ConvQA(CIS):
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
        super().__init__(params)
        self.logger.info("Conversational QA Model... starting up...")

    def generate_actions(self) -> dict:
        return {
            "retrieval": retrieval.get_retrieval_model(params=self.params),
            "qa": mrc.get_mrc_model(params=self.params)
        }

    def request_handler_func(self, conv_list: List[Message]) -> Message:
        """
        This function is called for each conversational interaction made by the user. It calls the NLP pipeline, DST
        model and all the actions and saves their result in the latest conversation message.

        Args:
            conv_list(list): List of Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.

        Returns:
            output_msg(Message): Returns an output message that should be sent to the UI to be presented to the user.
            It is the latest conversation message.
        """
        self.logger.info(conv_list)

        self.nlp_pipeline.run(conv_list)
        self.logger.info(f"nlp pipeline result: {conv_list[0].nlp_pipeline_result}")

        # Run the DST module and save the output in conversation.
        nlp_pipeline_output = conv_list[0].nlp_pipeline_result
        self.dialogue_manager.process_turn(nlp_pipeline_output)
        conv_list[0].dialog_manager = self.dialogue_manager

        dispatcher_output = self.request_dispatcher.dispatch(conv_list)

        output_msg = self.output_selection.get_output(conv_list, dispatcher_output)

        # Run response generator.
        models_to_run = self.response_generator_handler.models_selector(conv_list)
        rg_output = self.response_generator_handler.run_models(models_to_run, conv_list)
        self.logger.info(f"rg_output: {rg_output}")

        # TODO: Select or create response from RG output.

        conv_list[0].msg_info = output_msg.msg_info
        conv_list[0].response = output_msg.response
        conv_list[0].timestamp = output_msg.timestamp

        return conv_list[0]

    def run(self):
        """
        This function is called to run the ConvQA system. In live mode, it never stops until the program is killed.
        """
        self.interface.run()


if __name__ == "__main__":
    # Parse input arguments.
    parser = argparse.ArgumentParser(description="Run live_main.py file")
    parser.add_argument("--mode", type=str, default="live", help="live or exp (experimental)")
    parser.add_argument("--interface", type=str, default="stdio", help="can be 'telegram' or 'stdio' for live mode, and"
                                                                       " 'fileio' for exp mode")
    args = parser.parse_args()

    basic_params = {
        "timeout": 15,  # timeout is in terms of second.
        "mode": args.mode,  # mode can be either live or exp.
    }

    # for logging into file, pass the filepath to the Logger class.
    my_logger = LoggerFactory.create_logger({})

    # These are required database parameters if the mode is 'live'. The host and port of the machine hosting the
    # database, as well as the database name.
    db_params = {
        "interaction_db_host": "localhost",
        "interaction_db_port": 27017,
        "interaction_db_name": "macaw_test",
    }

    # These are interface parameters. They are interface specific.
    interface_params = {
        "interface": args.interface,  # interface can be 'telegram' or 'stdio' for live mode, and 'fileio'
        # for experimental mode.
        "input_file_path": "/usr/src/app/data/file_input.txt",
        "output_file_path": "/usr/src/app/data/file_output.txt",
        "output_format": "text",
        "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",  # Telegram bot token.
        # 'asr_model': 'google',  # The API used for speech recognition.
        # 'asg_model': 'google',  # The API used for speech generation.
        "google-speech-to-text-credential-file": "YOUR_GOOGLE_CREDENTIAL_FILE",
    }

    # These are parameters used by the retrieval model.
    retrieval_params = {
        "query_generation": "simple",  # the model that generates a query from a conversation history.
        "use_coref": True,  # True, if query generator can use coreference resolution, otherwise False.
        "search_engine": "tantivy",  # the search engine.
        "bing_key": "YOUR_BING_SUBSCRIPTION_KEY",  # Bing API key
        "search_engine_path": "tantivy_index/",  # The path to the tantivy index.
        "col_index": "/usr/src/app/indri-5.11/buildindex/my_index",  # The path to the indri index.
        "col_text_format": "trectext",  # collection text format. Standard 'trectext' is only supported.
        "results_requested": 3,
    }  # Maximum number of docs that should be retrieved by search engine.
    # Note: If you want to have a re-ranking model (e.g., learning to rank), you just need to simply extend the class
    # core.retrieval.search_engine.ReRanker and implement the method 'rerank'. Then simply add a 'reranker' parameter to
    # retrieval_params that points to an instance of your favorite ReRanker class. If there is a 'reranker' parameter in
    # retrieval_params, the retrieval model automatically calls the re-ranking method. For more details, see the method
    # 'get_results' in class core.retrieval.search_engine.Retrieval.

    # These are parameters used by the machine reading comprehension model.
    mrc_params = {
        "mrc": "drqa",  # MRC model.
        "mrc_model_path": "/usr/src/app/DrQA/data/reader/multitask.mdl",  # The path to the model parameters.
        "mrc_path": "/usr/src/app/DrQA",  # The path to the model toolkit.
        "corenlp_path": "/usr/src/app/stanford-corenlp-full-2017-06-09",  # The path to the corenlp toolkit.
        "qa_results_requested": 3,
    }  # The number of candidate answers returned by the MRC model.

    # ML modules which are part of the NLP pipeline and all response generators.
    ml_modules = {
        "nlp_models": {
            "intent_classification": "http://nlp-pipeline-app-ic:80",
            "sample_flask": "http://nlp-pipeline-app-flask:80",
        },
        "response_generator_models": {
            "qa": "http://response-generator-app-qa:80",
            "punctuation": ResponseGeneratorPunctuation(name="punctuation_model")
        }
    }

    params = {
        **basic_params,
        **db_params,
        **interface_params,
        **retrieval_params,
        **mrc_params,
        **ml_modules
    }

    my_logger.info(params)
    ConvQA(params).run()
