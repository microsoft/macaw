import argparse
import os
from typing import List

import tantivy

from macaw.core.retrieval.doc import get_trec_doc


def get_trec_docs(documents_path: str) -> List[str]:
    # can be optimized
    doc_list = []
    raw_body_list = []
    for trec_files in os.listdir(documents_path):
        if not trec_files.startswith('.'):
            with open(os.path.join(documents_path, trec_files), 'r', encoding="utf-8") as fobj:
                trec_txt = fobj.read()
                raw_body_list.append(trec_txt)
                doc_list.append(get_trec_doc(trec_txt))
    return doc_list, raw_body_list


def main(index_path, documents_path):
    # build the schema
    schema_builder = tantivy.SchemaBuilder()
    schema_builder.add_text_field("body", stored=True)
    schema_builder.add_unsigned_field("doc_id", stored=True)
    schema = schema_builder.build()
    # create index
    index = tantivy.Index(schema, path=index_path)
    # read all trec doc
    documents, raw_docs = get_trec_docs(documents_path)
    # add documents
    print('Building sparse index of {} docs...'.format(len(documents)))
    writer = index.writer()
    for i, doc in enumerate(raw_docs):
        writer.add_document(tantivy.Document(
            body=[doc],  # this is the raw text of the trec document
            doc_id=i
        ))
        if (i + 1) % 100000 == 0:
            writer.commit()
            print('Indexed {} docs'.format(i + 1))
    writer.commit()
    print('Built sparse index')
    index.reload()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Index documents')
    parser.add_argument('--index_path', type=str, help='path to store the index')
    parser.add_argument('--document_path', type=str, help='path for documents to index')
    args = parser.parse_args()

    main(args.index_path, args.document_path)
