"""
Some util functions.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

import json
import time

from stanfordcorenlp import StanfordCoreNLP


def current_time_in_milliseconds():
    """
    A method that returns the current time in milliseconds.

    Returns:
        An int representing the current time in milliseconds.
    """
    return int(round(time.time() * 1000))


class NLPUtil:
    def __init__(self, params):
        """
        A simple NLP helper class.

        Args:
            params(dict): A dict containing some parameters.
        """
        self.params = params
        self.corenlp = StanfordCoreNLP(self.params['corenlp_path'], quiet=False)

    def get_coref(self, text):
        """
        Run co-reference resolution on the input text.
        Args:
            text(str): It can be the concatenation of all conversation history.

        Returns:
            A json object containing all co-reference resolutions extracted from the input text.
        """
        props = {'annotators': 'coref', 'pipelineLanguage': 'en', 'ner.useSUTime': False}
        result = json.loads(self.corenlp.annotate(text, properties=props))
        return result
