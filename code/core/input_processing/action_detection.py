from code.core import actions

class RequestDispatcher:
    def __init__(self, params):
        self.params = params

    def action_detection(self, conv):
        if conv[0].msg_info['msg_type'] == 'command':
            command = conv[0].text.split(' ')[0]
            return command

        if 'qa' in self.params:
            if conv[0].text.endswith('?') \
                    or conv[0].text.lower().startswith('what') \
                    or conv[0].text.lower().startswith('who') \
                    or conv[0].text.lower().startswith('when') \
                    or conv[0].text.lower().startswith('where') \
                    or conv[0].text.lower().startswith('how') \
                    or conv[0].text.lower().startswith('is') \
                    or conv[0].text.lower().startswith('are'):
                return 'qa'
        if 'retrieval' in self.params:
            return 'retrieval'

    def dispatch(self, conv):
        action = self.action_detection(conv)
        if action == 'retrieval':
            return {'retrieval': actions.RetrievalAction.run(conv, self.params)}
        if action == 'qa':
            doc_list = actions.RetrievalAction.run(conv, self.params)
            qa_params = self.params
            for i in range(len(doc_list)):
                qa_params['doc'] = doc_list[i].text
                if len(doc_list[i].text.strip()) > 0:
                    break
            return {'qa': actions.QAAction.run(conv, qa_params)}
        if action == '#get_doc':
            doc_id = ' '.join(conv[0].text.split(' ')[1:])
            return {'#get_doc': actions.GetDocFromIndex.run(None, {**self.params, **{'doc_id': doc_id}})}