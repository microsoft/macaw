"""
The Indri search engine.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

import os
import subprocess

import pyndri

from macaw.core.retrieval.doc import get_trec_doc
from macaw.core.retrieval.search_engine import Retrieval


class Indri(Retrieval):
	def __init__(self, params):
		"""
		The Indri retrieval model. Indri is an open-source search engine implemented as part of the lemur project by
		UMass Amherst and CMU. Refer to http://lemurproject.org/indri.php for more information.
		The retrieval model used here is based on language modeling framework and retrieves documents using the query
		likelihood retrieval model [Ponte & Croft; SIGIR 1998] and Dirichlet prior smoothing [Zhai and Lafferty; SIGIR
		2001]. It is implemented using the Pyndri [Van Gysel et al.; ECIR 2017], which is a python interface to Indri.
		Refer to http://lemurproject.org/indri.php for more information on the Lemur toolkit.

		Args:
			params(dict): A dict containing some parameters. Here is the list of all required parameters:
			'indri_path': The path to the installed Indri toolkit.
			'index': The path to the Indri index constructed from the collection.
			'results_requested': The maximum number of requested documents for retrieval. If not given, it is set to 1.
			'text_format': The text format for document collection (e.g., 'trectext').
			Note that the parameters 'query_generation' and 'logger' are required by the parent class.
		"""
		super().__init__(params)
		self.results_requested = self.params['results_requested'] if 'results_requested' in self.params else 1
		self.indri_path = self.params['indri_path']
		self.index = pyndri.Index(self.params['index'])
		self.term2id, self.id2term, self.id2df = self.index.get_dictionary()
		self.id2tf = self.index.get_term_frequencies()

	def retrieve(self, query):
		"""
		This method retrieve documents in response to the given query.

		Args:
			query(str): The query string.

		Returns:
			A list of Documents with the maximum length of the 'results_requested' parameter.
		"""
		int_results = self.index.query(query, results_requested=self.results_requested)
		results = []
		for int_doc_id, score in int_results:
			# ext_doc_id, content_term_id = self.index.document(int_doc_id)
			# index_content = [self.id2term[term_id] if term_id> 0 else 'UNK' for term_id in content_term_id]
			doc = self.get_doc_from_index(int_doc_id)[0]
			doc.score = score
			doc.id = str(int_doc_id)
			results.append(doc)
		return results

	def get_doc_from_index(self, doc_id):
		"""
		This method retrieves a document content for a given document id.

		Args:
			doc_id(str): The document ID.

		Returns:
			A Document from the collection whose ID is equal to the given doc_id. For some reasons, the method returns
			a list of Documents with a length of 1.
		"""
		content = subprocess.run([os.path.join(self.indri_path, 'dumpindex/dumpindex'), self.params['index'],
								  'dt', str(doc_id)], stdout=subprocess.PIPE).stdout.decode('UTF-8')
		if self.params['text_format'] == 'trectext':
			doc = get_trec_doc(content)
		else:
			raise Exception('The requested text format is not supported!')
		return [doc]