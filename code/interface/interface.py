from abc import ABC, abstractmethod


class Interface(ABC):
    def __init__(self, params):
        self.params = params

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def result_presentation(self, response_msg, params):
        pass