from code.core.mrc import drqa_mrc


def get_mrc_model(params):
    if params['mrc'] == 'drqa':
        return drqa_mrc.DrQA(params)
    else:
        raise Exception('The requested MRC model does not exist!')