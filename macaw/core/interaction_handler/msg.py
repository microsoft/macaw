"""
The message used to represent each interaction in Macaw. It could be either from the user side or from the bot side.

Authors: Hamed Zamani (hazamani@microsoft.com), George Wei (gzwei@umass.edu)
"""
from datetime import datetime
from typing import Optional, Union, Dict

from .attributes import UserAttributes
from ..dialogue_manager.dialogue_manager import DialogManager


class Message:
    def __init__(
            self,
            user_interface: str,
            user_id: Union[str, int],
            text: str,
            timestamp: datetime,
            response: Optional[str] = None,
            user_info: Optional[Dict[str, any]] = None,
            msg_info: Optional[Dict[str, any]] = None,
            actions_result: Optional[Dict[str, any]] = None,
            dialog_manager: Optional[DialogManager] = None,
            nlp_pipeline_result: Optional[Dict[str, any]] = None,
            user_attributes: Optional[Dict[str, any]] = None,
    ):
        """
        An object for input and output Message.

        Args:
            user_interface(str): The interface name used for this message (e.g., 'telegram')
            user_id(str | int): The user ID.
            text(str): The user message text.
            response(str): (Optional) The bot message text. None indicates bot response hasn't been generated yet.
            timestamp(datetime.datetime): The timestamp of message.
            user_info(dict): (Optional) The dict containing some more information about the user.
            msg_info(dict): (Optional) The dict containing some more information about the message.
            actions_result(dict): (Optional) The results from the various actions given the conversation history.
            dialog_manager(DialogManager): (Optional) The dialog manager.
            nlp_pipeline_result(dict): (Optional) The results from running the NLP pipeline.
            user_attributes(dict): (Optional) The user attributes for this given message.
        """
        self.user_interface = user_interface
        self.user_id = user_id
        self.text = text
        self.response = response
        self.timestamp = timestamp
        self.user_info = user_info
        self.msg_info = msg_info
        self.actions_result = actions_result
        self.dialog_manager = dialog_manager
        self.nlp_pipeline_result = nlp_pipeline_result

        if user_attributes is None:
            user_attributes = dict()

        self.user_attributes = UserAttributes(**user_attributes)

    @classmethod
    def from_dict(cls, msg_dict):
        """
        Get a Message object from serialized dict obtained from database (e.g. MongoDB).
        Args:
            msg_dict(dict): A dict containing all the information required to construct a Message object.

        Returns:
            A Message object.
        """
        # Deserialize custom variables of Message class.
        msg_dict["dialog_manager"] = DialogManager.decode(msg_dict["dialog_manager"])

        return cls(**msg_dict)

    def __iter__(self):
        """
        This iterable is needed so that Message object can be inserted into a MongoDB table as a dictionary. It should
        provide encoding logic for all custom data types used inside Message class.
        """
        for attr, value in self.__dict__.items():
            value_ret = value
            if isinstance(value, UserAttributes):
                value_ret = value.__dict__
            elif isinstance(value, DialogManager):
                value_ret = value.encode()
            elif isinstance(value, datetime):
                value_ret = str(value)
            yield attr, value_ret
