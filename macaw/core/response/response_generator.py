from abc import ABC, abstractmethod


class ResponseGenerator(ABC):
    """
    An abstract class for response generator (RG). It can be implemented as a local RG using a local class or as a
    remote RG using a docker container to generate the response.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, conv_list) -> dict:
        pass
