from abc import ABC, abstractmethod
import os, sys

from code.core.retrieval.doc import Document
from drqa.reader import Predictor
import drqa


class MRC(ABC):
    @abstractmethod
    def __init__(self, params):
        self.params = params

    @abstractmethod
    def get_results(self, conv_list, doc):
        pass


class DrQA(MRC):
    def __init__(self, params):
        super().__init__(params)
        sys.path.insert(0, self.params['mrc_path'])
        drqa.tokenizers.set_default('corenlp_classpath', os.path.join(self.params['corenlp_path'], '*'))
        self.predictor = Predictor(self.params['mrc_model_path'], None, num_workers=0, normalize=False)

    def get_results(self, conv_list, doc):
        q = conv_list[0].text
        print('Question:', q)
        print('DOC:', doc)
        predictions = self.predictor.predict(doc, q, None, self.params['qa_results_requested'])
        results = []
        for i, p in enumerate(predictions, 1):
            results.append(Document(None, None, p[0], p[1]))
        return results




