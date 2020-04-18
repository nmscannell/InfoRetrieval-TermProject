from Index.Indexer import Indexer
from medsearch.models import Document


class QueryProcessor:
    def __init__(self):
        self.query = []
        self.index = Indexer().index

    def parse(self, query):
        self.query = Indexer.parse_string(query)
        self.query = [i for i in self.query if i in self.index]

    def perform_search(self):
        if len(self.query) == 0:
            raise Exception('No query has been made, or the terms are unknown.')

        postings = []
        for i in range(len(self.query)):
            postings.append(list(self.index[self.query[i]].keys()))
        common_docs = postings[0]
        for i in range(len(common_docs)):
            for j in range(1, len(postings)):
                if common_docs[i] not in postings[j]:
                    common_docs.remove(common_docs[i])
                    break
        if len(common_docs) > 0:
            docs = []
            for i in common_docs:
                docs.append(Document.objects.get(docID=i))
        else:
            docs = []
            for i in common_docs:
                for j in i:
                    docs.append(Document.objects.get(docID=j))

        pass
