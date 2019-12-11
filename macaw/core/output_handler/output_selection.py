"""
The output post processing unit.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

from abc import ABC, abstractmethod


class OutputProcessing(ABC):
    @abstractmethod
    def __init__(self, params):
        """
        The post-processing unit for producing the response message.

        Args:
            params(dict): A dict of parameters.
        """
        self.params = params

    @abstractmethod
    def get_output(self, conv, candidate_outputs):
        """
        The response message generator method.

        Args:
            conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
            candidate_outputs(dict): A dict of str (i.e., action) to list of Documents (i.e., the action's result) as
            the response. This dict is produced by action dispatcher, which means this is the aggregation of all the
            executed actions.

        Returns:
            A response Message to be sent to the user.
        """
        pass
