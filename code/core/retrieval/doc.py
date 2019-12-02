"""
The document class and some util functions useful for retrieval result list.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

import re

import justext


class Document:
    def __init__(self, id, title, text, score):
        """
            A simple class representing a document for retrieval.
        Args:
            id(str): Document ID.
            title(str): Document title (if any).
            text(str): Document content.
            score(float): The retrieval score.
        """
        self.id = id
        self.title = title
        self.text = text
        self.score = score


def get_recursive_content_as_str(doc):
    """
    THIS METHOD IS DEPRECATED!
    """
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


def get_trec_doc(trec_doc, format='trectext'):
    """
    This method returns a Document given a standard trectext or trecweb document. NOTE: There are much better parsers
    for TREC documents.
    Args:
        trec_doc(str): The document content with the trectext or trecweb format.
        format(str): The document format. Either 'trectext' or 'trecweb'. The default value is 'trectext'.

    Returns:
        An instance of Document. Note that the score is assigned to 0 and should be set later.
    """
    trec_doc_lower = trec_doc.lower()
    id = trec_doc[trec_doc_lower.find('<docno>') + len('<docno>'):trec_doc_lower.find('</docno>')].strip()
    title = id  # for some presentation reasons, the title of document is set to ids ID.
    if format == 'trectext':
        text = trec_doc[trec_doc_lower.find('<text>') + len('<text>'):trec_doc_lower.find('</text>')]
    elif format == 'trecweb':
        text = trec_doc[trec_doc_lower.find('<body>') + len('<body>'):trec_doc_lower.find('</body>')]
    else:
        raise Exception('Undefined TREC document format. Supported document formats are trectext and trecweb')
    text = re.sub('\s+', ' ', text).strip()  # removing multiple consecutive whitespaces

    # Removing other tags in the text, e.g., <p>.
    clean_text_list = []
    paragraphs = justext.justext(text, justext.get_stoplist("English"))
    for paragraph in paragraphs:
        if not paragraph.is_boilerplate:
            clean_text_list.append(paragraph.text)

    return Document(id, title, '\n'.join(clean_text_list), 0.)
