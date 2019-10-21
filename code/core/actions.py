from abc import ABC, abstractmethod


class Action(ABC):
    @staticmethod
    @abstractmethod
    def run(conv, params):
        pass


class RetrievalAction(Action):
    @staticmethod
    def run(conv, params):
        return params['retrieval'].get_results(conv)


class GetDocFromIndex(Action):
    @staticmethod
    def run(conv, params):
        return params['retrieval'].get_doc_from_index(params['doc_id'])


class QAAction(Action):
    @staticmethod
    def run(conv, params):
        return params['qa'].get_results(conv, params['doc'])