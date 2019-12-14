"""
Abstract classes for retrieval and ranking models.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

import requests

from macaw.core.retrieval.doc import Document
from macaw.core.retrieval.search_engine import Retrieval
from macaw.util.text_parser import html_to_clean_text


class BingWebSearch(Retrieval):
	def __init__(self, params):
		"""
		The Microsoft Bing Web search API. This class uses the Bing's API to get the retrieval results from the Web.
		Note that for some reasons, the results returned by the Bing API are usually different from the Bing search
		(without API).

		Args:
			params(dict): A dict containing some parameters. Here is the list of all required parameters:
			'bing_key': The Bing API key.
			'results_requested': The maximum number of requested documents for retrieval. If not given, it is set to 1.
			Note that this is limited by the number of results returned by the API.
		"""
		super().__init__(params)
		self.results_requested = self.params['results_requested'] if 'results_requested' in self.params else 1
		self.subscription_key = self.params['bing_key']
		self.bing_api_url = 'https://api.cognitive.microsoft.com/bing/v7.0/search'
		self.header = {"Ocp-Apim-Subscription-Key": self.subscription_key}
		params['logger'].warning('There is a maximum number of transactions per second for the Bing API.')

	def retrieve(self, query):
		"""
		This method retrieve documents in response to the given query.

		Args:
			query(str): The query string.

		Returns:
			A list of Documents with the maximum length of the 'results_requested' parameter.
		"""
		params = {"q": query, "textDecorations": True, "textFormat": "HTML"}
		response = requests.get(self.bing_api_url, headers=self.header, params=params)
		response.raise_for_status()
		search_results = response.json()
		results = []
		for i in range(min(len(search_results['webPages']['value']), self.results_requested)):
			id = search_results['webPages']['value'][i]['url']
			title = search_results['webPages']['value'][i]['name']
			snippet = search_results['webPages']['value'][i]['snippet']
			headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
			text = html_to_clean_text(requests.get(id, headers=headers).content)
			score = 10 - i  # this is not a score returned by Bing (just 10 - document rank)
			results.append(Document(id, title, text, score))
		return results

	def get_doc_from_index(self, doc_id):
		"""
		This method retrieves a document content for a given document id (i.e., URL).

		Args:
			doc_id(str): The document ID.

		Returns:
			A Document from the collection whose ID is equal to the given doc_id. For some reasons, the method returns
			a list of Documents with a length of 1.
		"""
		# Telegram has a nice interface for loading websites. Therefore, we decided to only pass the doc_id (URL). This
		# can be simply enhanced by the title and the content of the document.
		doc = Document(doc_id, doc_id, doc_id, -1)
		return [doc]