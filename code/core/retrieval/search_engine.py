from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import subprocess
import pyndri
import os
import requests

from code.core.retrieval.doc import get_trec_doc, Document
from code.util.text_parser import html_to_clean_text


class Retrieval(ABC):
	@abstractmethod
	def __init__(self, params):
		self.params = params
		self.query_generation = self.params['query_generation']

	@abstractmethod
	def retrieve(self, query):
		pass

	def get_results(self, conv_list):
		query = self.query_generation.get_query(conv_list)
		print('Query:', query)
		return self.retrieve(query)


class Indri(Retrieval):
	def __init__(self, params):
		super().__init__(params)
		self.results_requested = self.params['results_requested'] if 'results_requested' in self.params else 1
		self.indri_path = self.params['indri_path']
		self.index = pyndri.Index(self.params['index'])
		self.term2id, self.id2term, self.id2df = self.index.get_dictionary()
		self.id2tf = self.index.get_term_frequencies()

	def retrieve(self, query):
		int_results = self.index.query(query, results_requested=self.results_requested)
		results = []
		for int_doc_id, score in int_results:
			# ext_doc_id, content_term_id = self.index.document(int_doc_id)
			# index_content = [self.id2term[term_id] if term_id> 0 else 'UNK' for term_id in content_term_id]
			content = subprocess.run([os.path.join(self.indri_path, 'dumpindex/dumpindex'), self.params['index'],
										  'dt', str(int_doc_id)], stdout=subprocess.PIPE).stdout.decode('UTF-8')
			if self.params['text_format'] == 'trectext':
				doc = get_trec_doc(content)
			else:
				raise Exception('The requested text format is not supported!')
			doc.score = score
			doc.id = str(int_doc_id)
			results.append(doc)
		return results

	def get_doc_from_index(self, doc_id):
		content = subprocess.run([os.path.join(self.indri_path, 'dumpindex/dumpindex'), self.params['index'],
								  'dt', str(doc_id)], stdout=subprocess.PIPE).stdout.decode('UTF-8')
		if self.params['text_format'] == 'trectext':
			doc = get_trec_doc(content)
		else:
			raise Exception('The requested text format is not supported!')
		return [doc]


class BingWebSearch(Retrieval):
	def __init__(self, params):
		super().__init__(params)
		self.results_requested = self.params['results_requested'] if 'results_requested' in self.params else 1
		self.subscription_key = self.params['bing_key']
		self.bing_api_url = 'https://api.cognitive.microsoft.com/bing/v7.0/search'
		self.header = {"Ocp-Apim-Subscription-Key": self.subscription_key}

	def retrieve(self, query):
		params = {"q": query, "textDecorations": True, "textFormat": "HTML"}
		response = requests.get(self.bing_api_url, headers=self.header, params=params)
		response.raise_for_status()
		search_results = response.json()
		results = []
		for i in range(min(len(search_results['webPages']['value']), self.results_requested)):
			id = search_results['webPages']['value'][i]['url']
			title = search_results['webPages']['value'][i]['name']
			text = search_results['webPages']['value'][i]['snippet']
			text = ' '.join(BeautifulSoup(text, "html.parser").stripped_strings)
			print('************************ ', id)
			headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
			text = html_to_clean_text(requests.get(id, headers=headers).content)
			# print (response.content)
			score = 10 - i # this is not a score returned by Bing
			results.append(Document(id, title, text, score))
		return results

	def get_doc_from_index(self, doc_id):
		doc = Document(doc_id, doc_id, doc_id, -1)
		return [doc]
