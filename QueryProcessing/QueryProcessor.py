from Index.Indexer import Indexer
from medsearch.models import Document
from QueryProcessing import search
import math
import more_itertools


class QueryProcessor:
    def __init__(self, query):
        self.query = []
        self.query_string = query
        self.index = Indexer().index
        self.parse_query()

    def parse_query(self):
        if len(self.query_string) == 0:
            raise Exception('No query has been made.')
        if len(self.index) == 0:
            raise Exception('No index has been made.')
        self.query = Indexer.parse_string(self.query_string)
        self.query = [i for i in self.query if i in self.index]

    def perform_search(self):
        if len(self.query_string) == 0:
            raise Exception('No query has been made.')
        if len(self.index) == 0:
            raise Exception('No index has been made.')

        if len(self.query) == 0:
#            mes = 'No results found for query--searching Google.'
            results = search.perform_search(self.query_string)
            indexer = Indexer()
            indexer.index_google_results(results)
            self.index = indexer.index
            self.parse_query()
            return self.obtain_docs()

        mes, docs = self.obtain_docs()
        ranked = self.rank_docs(docs)
        return mes, ranked

    def rank_docs(self, docs):
        if len(self.index) == 0:
            raise Exception('No index has been made.')
        if len(docs) == 0:
            raise Exception('No documents to rank.')
        doc_scores = [0] * len(docs)
        # score depends on tf in title, tf in content, date if it exists****
        # TODO: incorporate date and source/type
        title_w = 0.5
        content_w = 0.3
        dates = [[i.docid, i.date] for i in docs]
        dates.sort(reverse=True, key=lambda e: e[1])

        # for each document, calculate the score based on tf-idf for each term in title and content
        for i in docs:
            for j in self.query:
                if i.docID not in self.index[j]:
                    continue
                title_tf = self.index[j][i.docID][0]
                content_tf = self.index[j][i.docID][1]
                idf = math.log(Indexer.num_docs/len(self.index[j]))
                doc_scores[i] += title_tf * title_w * idf + content_tf * content_w * idf

        # sort docs in descending order using the scores, then return title, url, summary of each doc in a list
        more_itertools.sort_together([doc_scores, docs], reverse=True)
        return docs

    def obtain_docs(self):
        if len(self.query_string) == 0:
            raise Exception('No query has been made.')
        if len(self.query) == 0:
            raise Exception('Query terms not in index.')
        if len(self.index) == 0:
            raise Exception('No index has been made.')
        postings = []
        for i in range(len(self.query)):
            postings.append(list(self.index[self.query[i]].keys()))

        # check what docs the terms have in common
        common_docs = postings[0]
        for i in range(len(common_docs)):
            for j in range(1, len(postings)):
                if common_docs[i] not in postings[j]:
                    common_docs.remove(common_docs[i])
                    break

        # if there are common terms, we will return results with both terms
        if len(common_docs) > 0:
            mes = 'Results contain both terms.'
            docs = []
            for i in common_docs:
                docs.append(Document.objects.get(docID=i))
        # otherwise, return docs that only contain one
        else:
            mes = 'No results found containing both terms. Results have one or more of query terms.'
            docs = []
            for i in postings:
                for j in i:
                    docs.append(Document.objects.get(docID=j))
        return mes, docs
