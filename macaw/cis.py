from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
import logging

from func_timeout import FunctionTimedOut

from core.response.handler import ResponseGeneratorHandler
from macaw import interface, util
from macaw.core.dialogue_manager.dialogue_manager import DialogManager
from macaw.core.response.action_detection import RequestDispatcher
from macaw.core.interaction_handler import CurrentAttributes
from macaw.core.interaction_handler.msg import Message
from macaw.core.interaction_handler.user_requests_db import InteractionDB
from macaw.core.nlp_pipeline.nlp_pipeline import NlpPipeline
from macaw.core.output_handler import naive_output_selection


class CIS(ABC):
    def __init__(self, params):
        """
        A Conversational Information Seeking class containing some abstract methods. Each CIS application is expected to
        be inherited from this class.

        Args:
            params(dict): A dict containing some parameters.
        """
        self.params = params
        if params["mode"] == "live":
            self.params["live_request_handler"] = self.live_request_handler
        elif params["mode"] == "exp":
            self.params["experimental_request_handler"] = self.file_request_handler

        self.msg_db = InteractionDB(
            host=self.params["interaction_db_host"],
            port=self.params["interaction_db_port"],
            dbname=self.params["interaction_db_name"],
        )

        self.logger = logging.getLogger("MacawLogger")
        self.params["curr_attrs"] = self.curr_attrs = CurrentAttributes()
        self.params["actions"] = self.generate_actions()
        self.interface = interface.get_interface(params)
        self.request_dispatcher = RequestDispatcher(self.params)
        self.output_selection = naive_output_selection.NaiveOutputProcessing({})
        self.dialogue_manager = DialogManager()
        self.nlp_pipeline = NlpPipeline(params.get("nlp_models", {}))
        self.response_generator_handler = ResponseGeneratorHandler(params.get("response_generator_models", {}))

        try:
            self.nlp_util = util.NLPUtil(self.params)
            self.params["nlp_util"] = self.nlp_util
        except Exception as ex:
            self.logger.warning(
                f"There is a problem with setting up the NLP utility module. {type(ex)}, {ex}"
            )
        self.timeout = self.params["timeout"] if "timeout" in self.params else -1

    def live_request_handler(self, msg: Message):
        try:
            # load conversation from the database.
            history = self.msg_db.get_conv_history(
                user_id=msg.user_id, max_time=10*60*1000, max_count=10
            )

            conv = [msg] + history

            # output_msg = func_timeout(self.timeout, self.request_handler_func, args=[conv])
            output_msg = self.request_handler_func(conv)

            # Save the output and conversation state in DB.
            self.msg_db.insert_one(output_msg)
            return output_msg

        except FunctionTimedOut:
            print(f"live_request_handler method timed out.")
            msg_info = dict()
            msg_info["msg_id"] = msg.msg_info["msg_id"]
            msg_info["msg_source"] = "system"
            msg_info["msg_type"] = "error"
            text = "Time out, no result!"
            timestamp = datetime.utcnow()
            error_msg = Message(
                user_interface=msg.user_interface,
                user_id=msg.user_id,
                user_info=msg.user_info,
                msg_info=msg_info,
                text=text,
                timestamp=timestamp,
            )
            self.msg_db.insert_one(error_msg)
            return error_msg

    def file_request_handler(self, msg: Message):
        # Just delegate the call to the live request handler.
        return self.live_request_handler(msg)

    @abstractmethod
    def request_handler_func(self, conv_list: List[Message]) -> Message:
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def generate_actions(self) -> dict:
        pass
