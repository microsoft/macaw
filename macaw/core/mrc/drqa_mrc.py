import os
import sys
from abc import ABC, abstractmethod

import drqa
from drqa.reader import Predictor

"""
A wrapper to the DrQA model from FAIR: https://github.com/facebookresearch/DrQA 

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

from macaw.core.retrieval.doc import Document


class MRC(ABC):
    @abstractmethod
    def __init__(self, params):
        """
        An abstract class for machine reading comprehension models implemented in Macaw.

        Args:
            params(dict): A dict containing some mandatory and optional parameters.
        """
        self.params = params

    @abstractmethod
    def get_results(self, conv_list, doc):
        """
            This method is called to get the answer(s) to a question.

        Args:
            conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
            doc(Document): A document (core.retrieval.doc.Document) that potentially contains the answer.

        Returns:
            The inherited class should implements this method and return a list of Documents each containing a candidate
            answer and its confidence score.
        """
        pass


class DrQA(MRC):
    def __init__(self, params):
        """
        A machine reading comprehension model based on DrQA (https://github.com/facebookresearch/DrQA).

        Args:
            params(dict): A dict of parameters. Required parameters are:
            'mrc_path': The path to the DrQA repository.
            'corenlp_path': The path to the Stanford's corenlp toolkit. DrQA requires corenlp.
            'mrc_model_path': The path to the learned DrQA parameters.
            'qa_results_requested': The maximum number of candidate answers that should be found by DrQA.
        """
        super().__init__(params)
        sys.path.insert(0, self.params['mrc_path'])
        drqa.tokenizers.set_default('corenlp_classpath', os.path.join(self.params['corenlp_path'], '*'))
        self.predictor = Predictor(self.params['mrc_model_path'], tokenizer='simple', num_workers=0, normalize=False)

    def get_results(self, conv_list, doc):
        """
        This method returns the answers to the question.

        Args:
            conv_list(list): List of util.msg.Message, each corresponding to a conversational message from / to the
            user. This list is in reverse order, meaning that the first elements is the last interaction made by user.
            doc(Document): A document (core.retrieval.doc.Document) that potentially contains the answer.

        Returns:
            Returns a list of Documents each containing a candidate answer and its confidence score. The length of this
            list is less than or equal to the parameter 'qa_results_requested'.
        """
        q = conv_list[0].text
        predictions = self.predictor.predict(doc, q, None, self.params['qa_results_requested'])
        results = []
        for i, p in enumerate(predictions, 1):
            results.append(Document(None, None, p[0], p[1]))
        return results
