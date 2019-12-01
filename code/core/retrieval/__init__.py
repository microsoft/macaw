"""
The retrieval module init.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

from code.core.retrieval import search_engine, query_generation


def get_retrieval_model(params):
    """
    This method returns the Retrieval class requested in the parameter dict.
    Args:
        params(dict): A dict of parameters. In this method, the parameters 'logger' and 'query_generation', and
        'search_engine' are required. Based on the requested retrievel model, some more parameters may be mandatory.
        Currently, Macaw serves two different search engines. One is based on indri (http://lemurproject.org/indri.php),
        and the other one is the Microsoft Bing API. If you want to retrieve results from your own document collection,
        indri is a useful search engine, otherwise you can rely on the Bing's Web search.

    Returns:
        A Retrieval object for document retrieval.
    """
    params['logger'].info('The query generation model for retrieval: ' + params['query_generation'])
    if params['query_generation'] == 'simple':
        q_generation = query_generation.SimpleQueryGeneration(params)
    else:
        raise Exception('The requested query generation model does not exist!')

    params['logger'].info('The search engine for retrieval: ' + params['search_engine'])
    if params['search_engine'] == 'indri':
        return search_engine.Indri({'query_generation': q_generation,
                                    'indri_path': params['search_engine_path'],
                                    'index': params['col_index'],
                                    'text_format': params['col_text_format'],
                                    'results_requested': params['results_requested'],
                                    'logger': params['logger']})
    elif params['search_engine'] == 'bing':
        return search_engine.BingWebSearch({'query_generation': q_generation,
                                            'bing_key': params['bing_key'],
                                            'results_requested': params['results_requested'],
                                            'logger': params['logger']})
    else:
        raise Exception('The requested retrieval model does not exist!')