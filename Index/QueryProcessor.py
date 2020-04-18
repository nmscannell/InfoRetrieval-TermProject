from Index.Indexer import Indexer

class QueryProcessor:
    def __init__(self):
        self.query = []
        self.index = Indexer().index

    def parse(self, query):
        self.query = Indexer.parse_string(query)

    def perform_search(self):
        pass
