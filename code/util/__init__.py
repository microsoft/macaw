import time
import json
from stanfordcorenlp import StanfordCoreNLP

def current_time_in_milliseconds():
    return int(round(time.time() * 1000))


class NLPUtil:
    def __init__(self, params):
        self.params = params
        self.corenlp = StanfordCoreNLP(self.params['corenlp_path'], quiet=False)

    def get_coref(self, text):
        props = {'annotators': 'coref', 'pipelineLanguage': 'en', 'ner.useSUTime': False}
        result = json.loads(self.corenlp.annotate(text, properties=props))
        return result
