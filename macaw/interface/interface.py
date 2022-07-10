"""
The abstract interface class.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

from abc import ABC, abstractmethod

from core.interaction_handler import Message


class Interface(ABC):
    def __init__(self, params):
        self.params = params

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def result_presentation(self, response_msg: Message, additional_params: dict):
        pass
