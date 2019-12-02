"""
Some text parser for document cleaning.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

import justext
from xml.etree import cElementTree as ElementTree


class XmlListConfig(list):
    def __init__(self, aList):
        """
        THIS CLASS IS DEPRECATED!
        """
        super().__init__()
        for element in aList:
            if element:
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    def __init__(self, parent_element):
        """
        THIS CLASS IS DEPRECATED!
        """
        super().__init__()
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                else:
                    aDict = {element[0].tag: XmlListConfig(element)}
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            elif element.items():
                self.update({element.tag: dict(element.items())})
            else:
                self.update({element.tag: element.text})


def xml_text_to_dict(xml_text):
    """
    THIS CLASS IS DEPRECATED!
    """
    print(xml_text)
    root = ElementTree.XML(xml_text)
    return XmlDictConfig(root)


def xml_file_to_dict(xml_file):
    """
    THIS CLASS IS DEPRECATED!
    """
    tree = ElementTree.parse(xml_file)
    root = tree.getroot()
    return XmlDictConfig(root)


# def html_to_clean_text(html):
#     """
#     Converting an HTML document to clean text.
#     Args:
#         html(str): The content of an HTML web page.
#
#     Returns:
#         A str containing the clean content of the web page.
#     """
#     def visible(element):
#         if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
#             return False
#         elif re.match('<!--.*-->', str(element.encode('utf-8'))):
#             return False
#         return True
#
#     soup = BeautifulSoup(html, features='html.parser') #.stripped_strings
#     data = soup.findAll(text=True)
#     result = filter(visible, data)
#     return ' '.join(result)

def html_to_clean_text(html):
    """
    Converting an HTML document to clean text.
    Args:
        html(str): The content of an HTML web page.

    Returns:
        A str containing the clean content of the web page.
    """
    paragraphs = justext.justext(html, justext.get_stoplist("English"))
    clean_text_list = []
    for paragraph in paragraphs:
        if not paragraph.is_boilerplate:
            clean_text_list.append(paragraph.text)
    return '\n'.join(clean_text_list)
