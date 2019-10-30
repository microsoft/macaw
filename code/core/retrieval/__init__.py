from code.core.retrieval import search_engine, query_generation


def get_retrieval_model(params):
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
                                    'results_requested': params['results_requested']})
    elif params['search_engine'] == 'bing':
        return search_engine.BingWebSearch({'query_generation': q_generation,
                                            'bing_key': params['bing_key'],
                                            'results_requested': params['results_requested']})
    else:
        raise Exception('The requested retrieval model does not exist!')