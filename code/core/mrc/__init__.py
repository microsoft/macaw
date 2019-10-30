from code.core.mrc import drqa_mrc


def get_mrc_model(params):
    params['logger'].info('The MRC model for QA: ' + params['mrc'])
    if params['mrc'] == 'drqa':
        return drqa_mrc.DrQA(params)
    else:
        raise Exception('The requested MRC model does not exist!')