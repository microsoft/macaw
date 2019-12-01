"""
The MRC module init.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

from code.core.mrc import drqa_mrc


def get_mrc_model(params):
    """
    This method returns the MRC class requested in the parameter dict.
    Args:
        params(dict): A dict of parameters. In this method, the parameters 'logger' and 'mrc' are required. Currently,
        only one MRC model (i.e., 'drqa') is implemented.

    Returns:
        An MRC object for machine reading comprehension.
    """
    params['logger'].info('The MRC model for QA: ' + params['mrc'])
    if params['mrc'] == 'drqa':
        return drqa_mrc.DrQA(params)
    else:
        raise Exception('The requested MRC model does not exist!')

