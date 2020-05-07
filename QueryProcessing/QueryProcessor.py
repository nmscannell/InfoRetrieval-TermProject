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

        rank.sort(key=lambda e: e[0])
        for i in range(len(rank)-1):
            if i > len(rank)-1:
                break
            while i+1 < len(rank) and rank[i][0] == rank[i+1][0]:
                score = rank[i][1] + rank[i+1][1]
                rank[i] = (rank[i][0], score)
                rank.remove(rank[i+1])

        common_rank.sort(reverse=True, key=lambda e: e[1])
        rank.sort(reverse=True, key=lambda e: e[1])
        return common_rank, rank

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
                    if self.source == 'all' or self.source == v['source']:
                        keys.append(k)
                        p.append((k, v))
                if len(keys) > 0:
                    bi_keys.append(keys)
                if len(p) > 0:
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
                    if self.source == 'all' or self.source == v['source']:
                        keys.append(k)
                        p.append((k, v))
                if len(p) > 0:
                    postings.append(p)
                if len(keys) > 0:
                    p_keys.append(keys)

        common_docs = self.find_common_docs(p_keys)
        # check what docs the terms have in common

        bi_ranked_c, bi_ranked_n = self.rank_docs(common_bi_docs, bi_post)
        all_ranked_c, all_ranked_n = self.rank_docs(common_docs, postings)

        # get ranked docs and return
        docs = []
        for pair in bi_ranked_c:
            docs.append(Document.objects.get(docID=pair[0]))
        for pair in all_ranked_c:
            docs.append(Document.objects.get(docID=pair[0]))
        for pair in bi_ranked_n:
            docs.append(Document.objects.get(docID=pair[0]))
        for pair in all_ranked_n:
            docs.append(Document.objects.get(docID=pair[0]))

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
        return docs[:20]

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
