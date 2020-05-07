from Index.Indexer import Indexer
from medsearch.models import Document
from QueryProcessing import search
import math
import more_itertools


class QueryProcessor:
    def __init__(self, query, source):
        self.indexer = Indexer()
        self.query = []
        self.query_string = query
        self.index = self.indexer.index
        self.source = source
        self.parse_query()

    def parse_query(self):
        if len(self.query_string) == 0:
            raise Exception('No query has been made.')
        if len(self.index) == 0:
            raise Exception('No index has been made.')
        self.query = self.indexer.parse_string(self.query_string)
        self.query = [i for i in self.query if i in self.index]

    def perform_search(self):
        if len(self.query_string) == 0:
            raise Exception('No query has been made.')
        if len(self.index) == 0:
            raise Exception('No index has been made.')

        if len(self.query) == 0:
            results = search.perform_search(self.query_string)
            self.indexer.index_google_results(results)
            self.index = self.indexer.index
            self.parse_query()
            return self.obtain_docs()

        ranked = self.obtain_docs()
        if len(ranked) > 20:
            ranked = ranked[:20]
        return ranked

    def rank_docs(self, common, docs):
        # common is a list of common doc IDs
        # docs is a list of lists of key-value pairs, doc ID-values for each term
        if len(self.index) == 0:
            raise Exception('No index has been made.')
        if len(docs) == 0:
            raise Exception('No documents to rank.')
        doc_scores = [0] * len(common)
        # score depends on tf in title, tf in content, type
        title_w = 0.4
        content_w = 0.3
        source_w = 0.3

        common_rank = []
        for ids in common:
            score = 0
            for i in range(len(docs)):
                idf = math.log(self.indexer.num_docs/len(docs[i]))
                for pair in docs[i]:
                    if pair[0] == ids:
                        score += title_w * idf * pair[1]['title']
                        score += content_w * idf * pair[1]['body']
                        if pair[1]['source'] == 'experiment' or pair[1]['source'] == 'research':
                            score += source_w
                        elif pair[1]['source'] == 'medical':
                            score += source_w * .75
                        elif pair[1]['source'] == 'book':
                            score += source_w * .5
            common_rank.append((ids, score))

        rank = []
        for i in range(len(docs)):
            idf = math.log(self.indexer.num_docs / len(docs[i]))
            for pair in docs[i]:
                if pair[0] not in common:
                    score = 0
                    score += title_w * idf * pair[1]['title']
                    score += content_w * idf * pair[1]['body']
                    if pair[1]['source'] == 'experiment' or pair[1]['source'] == 'research':
                        score += source_w
                    elif pair[1]['source'] == 'medical':
                        score += source_w * .75
                    elif pair[1]['source'] == 'book':
                        score += source_w * .5
                    rank.append((pair[0], score))


        # for each document, calculate the score based on tf-idf for each term in title and content

        for i in range(len(docs)):
            for j in self.query:
                if docs[i].docID not in self.index[j]:
                    continue
                title_tf = self.index[j][docs[i].docID][0]
                content_tf = self.index[j][docs[i].docID][1]
                idf = math.log(self.indexer.num_docs/len(self.index[j]))
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

        bi_grams = []
        prev = None
        for i in self.query:
            if prev is not None:
                bi_grams.append(prev + ' ' + i)
            prev = i

        bi_post = []
        bi_keys = []
        for i in bi_grams:
            if i in self.index:
                p = []
                keys = []
                for k, v in self.index[i].items():
                    keys.append(k)
                    p.append((k, v))
                bi_keys.append(keys)
                bi_post.append(p)

        # do something with bi_post
        common_bi_docs = self.find_common_docs(bi_keys)

        postings = []
        p_keys = []
        for i in self.query:
            if i in self.index:
                p = []
                keys = []
                for k, v in self.index[i].items():
                    keys.append(k)
                    p.append((k, v))
                postings.append(p)
                p_keys.append(keys)

        common_docs = self.find_common_docs(p_keys)
        # check what docs the terms have in common

        bi_ranked = self.rank_docs(common_bi_docs, bi_post)
        all_ranked = self.rank_docs(common_docs, postings)

        # get ranked docs and return
        docs = []
        '''
        # if there are common terms, we will return results with both terms
        if len(common_docs) > 0:
            mes = 'Results contain all terms.'
            docs = []
            for i in common_docs:
                if self.source == 'all':
                    docs.append(Document.objects.get(docID=i))
                else:
                    d = Document.objects.get(docID=i)
                    if d.type == self.source:
                        docs.append(d)
        # otherwise, return docs that only contain one
        else:
            mes = 'No results found containing both terms. Results have one or more of query terms.'
            docs = []
            for i in postings:
                for j in i:
                    docs.append(Document.objects.get(docID=j))
        '''
        return docs

    @staticmethod
    def find_common_docs(postings):
        common = postings[0]

        for i in range(1, len(postings)):
            if len(common) == 0:
                break
            for e in common:
                if len(common) == 0:
                    break
                if e not in postings[i]:
                    common.remove(e)

        return common
