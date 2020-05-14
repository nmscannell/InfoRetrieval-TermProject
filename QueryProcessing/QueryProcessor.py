from Index.Indexer import Indexer
from medsearch.models import Document
from QueryProcessing import search
import math


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
            # results = search.perform_search(self.query_string)
            mes = 'No documents contain your query'
            return mes, []

        ranked = self.obtain_docs()
        return None, ranked

    def rank_docs(self, common, docs):
        # common is a list of common doc IDs
        # docs is a list of lists of key-value pairs, doc ID-values for each term
        if len(self.index) == 0:
            raise Exception('No index has been made.')
        if len(docs) == 0:
            return None, None

        # score depends on tf in title, tf in content, type
        title_w = 0.4
        content_w = 0.3
        source_w = 0.3

        common_rank = []
        print('common')
        for ids in common:
            print(ids)
            score = 0
            for i in range(len(docs)):
                idf = math.log(self.indexer.num_docs/len(docs[i]))
                for pair in docs[i]:
                    if pair[0] == ids:
                        print(pair[1])
                        if 'title' in pair[1]:
                            score += title_w * idf * pair[1]['title']
                        if 'body' in pair[1]:
                            score += content_w * idf * pair[1]['body']
                        if pair[1]['type'] == 'experiment' or pair[1]['type'] == 'research':
                            score += source_w
                        elif pair[1]['type'] == 'medical':
                            score += source_w * .75
                        elif pair[1]['type'] == 'book':
                            score += source_w * .5
            common_rank.append((ids, score))

        rank = []
        print('not')
        for i in range(len(docs)):
            idf = math.log(self.indexer.num_docs / len(docs[i]))
            for pair in docs[i]:
                if pair[0] not in common:
                    print(pair[0], pair[1])
                    score = 0
                    if 'title' in pair[1]:
                        score += title_w * idf * pair[1]['title']
                    if 'body' in pair[1]:
                        score += content_w * idf * pair[1]['body']
                    if pair[1]['type'] == 'experiment' or pair[1]['type'] == 'research':
                        score += source_w
                    elif pair[1]['type'] == 'medical':
                        score += source_w * .75
                    elif pair[1]['type'] == 'book':
                        score += source_w * .5
                    rank.append((pair[0], score))

        rank.sort(key=lambda e: e[0])
        for i in range(len(rank)-1):
            if i > len(rank)-2:
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
            print(i)
            if i in self.index:
                print('bigram in index')
                p = []
                keys = []
                for k, v in self.index[i].items():
                    print(k)
                    if self.source == 'all' or self.source == v['type']:
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
            print(i)
            if i in self.index:
                print('in index')
                p = []
                keys = []
                for k, v in self.index[i].items():
                    print(k, v)
                    if self.source == 'all' or self.source == v['type']:
                        keys.append(k)
                        p.append((k, v))
                if len(p) > 0:
                    postings.append(p)
                if len(keys) > 0:
                    p_keys.append(keys)

        common_docs = self.find_common_docs(p_keys)
        # check what docs the terms have in common
        print(common_docs)

        bi_ranked_c, bi_ranked_n = self.rank_docs(common_bi_docs, bi_post)
        all_ranked_c, all_ranked_n = self.rank_docs(common_docs, postings)

        print(bi_ranked_c)
        print(bi_ranked_n)
        print(all_ranked_c)
        print(all_ranked_n)
        # get ranked docs and return
        docs = []
        ids = []
        if bi_ranked_c is not None:
            for pair in bi_ranked_c:
                print(pair[0])
                if pair[0] not in ids:
                    ids.append(pair[0])
                    docs.append(Document.objects.get(docID=pair[0]))
        if bi_ranked_n is not None:
            for pair in bi_ranked_n:
                print(pair[0])
                if pair[0] not in ids:
                    ids.append(pair[0])
                    docs.append(Document.objects.get(docID=pair[0]))
        if all_ranked_c is not None:
            for pair in all_ranked_c:
                print(pair[0])
                if pair[0] not in ids:
                    ids.append(pair[0])
                    docs.append(Document.objects.get(docID=pair[0]))
        if all_ranked_n is not None:
            for pair in all_ranked_n:
                print(pair[0])
                if pair[0] not in ids:
                    ids.append(pair[0])
                    docs.append(Document.objects.get(docID=pair[0]))
        if len(ids) > 20:
            ids = ids[:20]
        print('printing ids')
        for i in ids:
            print(i)
        if len(docs) > 20:
            docs = docs[:20]
        return docs

    @staticmethod
    def find_common_docs(postings):
        if len(postings) == 0:
            return

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
