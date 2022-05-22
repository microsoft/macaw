"""
The Indri search engine.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

import os
import subprocess

import tantivy

from macaw.core.retrieval.doc import get_trec_doc
from macaw.core.retrieval.search_engine import Retrieval


class Tantivy(Retrieval):
    def __init__(self, params):
        super().__init__(params)
        self.results_requested = self.params['results_requested'] if 'results_requested' in self.params else 1

        if not os.path.exists(params['path']):
            os.mkdir(params['path'])
        schema_builder = tantivy.SchemaBuilder()
        schema_builder.add_text_field("body", stored=True)
        schema_builder.add_unsigned_field("doc_id", stored=True)
        schema = schema_builder.build()
        self.index = tantivy.Index(schema, path=params['path'], reuse=params['load'])
        self.searcher = self.index.searcher()

    def retrieve(self, query):
        results = []
        docs = []
        try:
            query = self.index.parse_query(query, ["body"])
            scores = self.searcher.search(query, self.results_requested).hits
            # docs = [(self.searcher.doc(doc_id)['doc_id'], score) for score, doc_id in scores]
            docs = [self.searcher.doc(doc_id)['doc_id'] for _, doc_id in scores]
        except:
            pass
        results.append(docs)

        return results

    def get_doc_from_index(self, doc_id):
        return [self.searcher.doc(doc_id)['body']]