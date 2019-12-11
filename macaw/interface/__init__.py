"""
The interface module init.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

from macaw.interface import speech_recognition, telegram, stdio, fileio


def get_interface(params):
    if 'asr_model' in params and params['asr_model'] == 'google':
        params['asr'] = speech_recognition.GoogleASR(params)
    if 'asg_model' in params and params['asg_model'] == 'google':
        params['asg'] = speech_recognition.GoogleText2Speech(params)

    if params['interface'] == 'telegram':
        return telegram.TelegramBot(params)
    elif params['interface'] == 'stdio':
        return stdio.StdioInterface(params)
    elif params['interface'] == 'fileio':
        return fileio.FileioInterface(params)
    else:
        raise Exception('The requested interface does not exist!')