"""
The message used to represent each interaction in Macaw.

Authors: Hamed Zamani (hazamani@microsoft.com), George Wei (gzwei@umass.edu)
"""
from datetime import datetime
from typing import Optional, Union, Dict

from .attributes import UserAttributes


class Message:
    def __init__(
        self,
        user_interface: str,
        user_id: Union[str, int],
        text: str,
        timestamp: datetime,
        user_info: Optional[Dict[str, any]] = None,
        msg_info: Optional[Dict[str, any]] = None,
        actions: Optional[Dict[str, any]] = None,
        dialog_state_tracking: Optional[Dict[str, any]] = None,
        nlp_pipeline: Optional[Dict[str, any]] = None,
        user_attributes: Optional[Dict[str, any]] = None,
    ):
        """
        An object for input and output Message.

        Args:
            user_interface(str): The interface name used for this message (e.g., 'telegram')
            user_id(str | int): The user ID.
            text(str): The message text.
            timestamp(datetime.datetime): The timestamp of message.
            user_info(dict): (Optional) The dict containing some more information about the user.
            msg_info(dict): (Optional) The dict containing some more information about the message.
            actions(dict): (Optional) The results from the various actions given the conversation history.
            dialog_state_tracking(dict): (Optional) The dialog state tracking dict.
            nlp_pipeline(dict): (Optional) The results from running the NLP pipeline.
            user_attributes(dict): (Optional) The user attributes for this given message.
        """
        self.user_interface = user_interface
        self.user_id = user_id
        self.text = text
        self.timestamp = timestamp
        self.user_info = user_info
        self.msg_info = msg_info
        self.actions = actions
        self.dialog_state_tracking = dialog_state_tracking
        self.nlp_pipeline = nlp_pipeline

        if user_attributes is None:
            user_attributes = dict()

        self.user_attributes = UserAttributes(**user_attributes)

    @classmethod
    def from_dict(cls, msg_dict):
        """
        Get a Message object from dict.
        Args:
            msg_dict(dict): A dict containing all the information required to construct a Message object.

        Returns:
            A Message object.
        """
        return cls(**msg_dict)

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value if not isinstance(
                value, UserAttributes
            ) else value.__dict__  # If this doesn't work, default to `None`
