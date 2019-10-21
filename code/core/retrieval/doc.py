from code.util.text_parser import xml_text_to_dict

class Document:
    def __init__(self, id, title, text, score):
        self.id = id
        self.title = title
        self.text = text
        self.score = score


def get_recursive_content_as_str(doc):
    text = ''
    if isinstance(doc, str):
        return doc.strip() + '\n'
    elif isinstance(doc, dict):
        for key in doc:
            text += get_recursive_content_as_str(doc[key])
    elif isinstance(doc, list):
        for t in doc:
            text += get_recursive_content_as_str(t)
    else:
        raise Exception('cannot parse document recursively, ' + str(type(doc)))
    return text


# def get_trec_doc(doc):
#     doc_dict = xml_text_to_dict(doc)
#     id = doc_dict['DOCNO']
#     title = None
#     text = get_recursive_content_as_str(doc_dict['TEXT'])
#     return Document(id, title, text, 0)


def get_trec_doc(doc):
    title = doc[doc.find('<DOCNO>')+len('<DOCNO>'):doc.find('</DOCNO>')].strip()
    text = doc[doc.find('<TEXT>') + len('<TEXT>'):doc.find('</TEXT>')].replace('<P>', ' ').replace('</P>', '\n').strip()
    return Document(id, title, text, 0)
