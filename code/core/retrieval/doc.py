
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


def get_trec_doc(trec_doc):
    """
    This method returns a Document given a standard trectext document. NOTE: There are much better parsers for TREC
    documents. This simple function works in most cases, but there might be some cases that require better parsers
    (e.g., when there is a HTML-type comments in the text, or some other tags other than <P>.)
    Args:
        trec_doc(str): The document content with the trectext format.

    Returns:
        An instance of Document. Note that the score is assigned to 0 and should be set later.
    """
    id = trec_doc[trec_doc.find('<DOCNO>') + len('<DOCNO>'):trec_doc.find('</DOCNO>')].strip()
    title = id  # for some presentation reasons, the title of document is set to ids ID.
    text = trec_doc[trec_doc.find('<TEXT>') + len('<TEXT>'):trec_doc.find('</TEXT>')]\
        .replace('<P>', ' ').replace('</P>', '\n').strip()
    return Document(id, title, text, 0.)
