"""
Some util functions.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

import json

import backoff as backoff
from stanfordcorenlp import StanfordCoreNLP


class NLPUtil:
    @backoff.on_exception(backoff.expo,
                          Exception,
                          max_tries=3)
    def __init__(self, params):
        """
        A simple NLP helper class.

        Args:
            params(dict): A dict containing some parameters.
        """
        self.params = params
        self.corenlp = StanfordCoreNLP(self.params["corenlp_path"], quiet=False)

        # Pre-fetching the required models.
        props = {
            "annotators": "coref",
            "pipelineLanguage": "en",
            "ner.useSUTime": False,
        }
        self.corenlp.annotate("", properties=props)

    def get_coref(self, text):
        """
        Run co-reference resolution on the input text.
        Args:
            text(str): It can be the concatenation of all conversation history.

        Returns:
            A json object containing all co-reference resolutions extracted from the input text.
        """
        props = {
            "annotators": "coref",
            "pipelineLanguage": "en",
            "ner.useSUTime": False,
        }
        result = json.loads(self.corenlp.annotate(text, properties=props))

        return result
