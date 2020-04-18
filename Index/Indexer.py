import nltk
import requests
from nltk.corpus import stopwords
from medsearch.models import Document
import pickle
import os.path
from bs4 import BeautifulSoup as bs

'''
Indexer parses and stores data in the database.
Data pulled from xlsx file or from web scraper.
All terms are lowercased, punctuation and stop words are removed.

Inverted index contains search terms with postings lists that contains term frequency for each docID
Inverted index is stored in a dict that is saved and loaded via pickle.
'''


class Indexer():
    def __init__(self):
        if os.path.exists('Index/obj/index.pkl'):
            print('index exists')
            self.index = Indexer.load_obj('index')
        else:
            print('no index')
            self.index = {}
        self.punct = ['.', '?', '"', ',', "'", '+', '%', '!', "''"]
        self.stops = stopwords.words('english')
        self.num_docs = len(Document.objects.all())
        if os.path.exists('obj/scraped.pkl'):
            self.scraped = Indexer.load_obj('scraped')
        else:
            self.scraped = []

    def process_file(self, file, doc_id):
        with open(file) as f:
            url = f.readline().strip('\n')
            type = f.readline().strip('\n')
            title = f.readline().strip('\n')
            date = f.readline().strip('\n')
            content = ''
            for l in f.readlines():
                content += l.strip('\n').strip() + ' '
        p_title = self.parse_string(title)
        p_content = self.parse_string(content)
        # doc_id = self.num_docs

        for i in p_title:
            self.add_to_index(i, doc_id)

        for i in p_content:
            self.add_to_index(i, doc_id, False)

        if len(content) > 800:
            content = content[:800] + '...'
        self.store_doc(doc_id, url, type, title, content, date)

    def add_to_index(self, i, doc_id, title=True):
        if title:
            if i in self.index:
                if doc_id in self.index[i]:
                    self.index[i][doc_id][0] = self.index[i][doc_id][0] + 1
                else:
                    self.index[i][doc_id] = [1, 0]
            else:
                self.index[i] = {doc_id: [1, 0]}
        else:
            if i in self.index:
                if doc_id in self.index[i]:
                    self.index[i][doc_id][1] = self.index[i][doc_id][1] + 1
                else:
                    self.index[i][doc_id] = [0, 1]
            else:
                self.index[i] = {doc_id: [0, 1]}
#        self.num_docs += 1
        Indexer.save_obj(self.index, 'index')

    def parse_string(self, string):
        res = nltk.word_tokenize(string.lower())
        res = [i for i in res if i not in stopwords.words('english') and not any(c.isdigit() for c in i)]
        res = list(filter(lambda i: i not in self.punct, res))
        for i in range(len(res)):
            if res[i] == "n't":
                res[i] = 'not'
            res[i] = res[i].strip('.!?",/\\*()-_&;~:[]{}')
            if res[i].count('/') > 0 and res[i].count('.com') == 0:
                words = res[i].split('/')
                res[i] = words[0]
                for j in range(1, len(words)):
                    res.append(words[j])
            if res[i].count('.') > 0 and res[i].count('.com') == 0:
                words = res[i].split('.')
                res[i] = words[0]
                for j in range(1, len(words)):
                    res.append(words[j])
        return res

    def scrape_web(self, url, doc_id):
        if url in self.scraped:
            return
#        doc_id = self.num_docs
        page = requests.get(url)
        soup = bs(page.content, 'html.parser')
        content = ''
        if url.count('nasa.gov') > 0:
            if url.count('/experiments/') > 0:
                type = 'research'
                date = '*'
                title = soup.find(class_='inv-title').get_text().strip()
                content += soup.find(class_='block flagged').get_text().strip() + ' '
                content += soup.find(id='ResearchSummary').get_text().strip() + ' '
                content += soup.find(id='ResearchDescription').get_text().strip() + ' '
                content += soup.find(id='ApplicationsInSpaceAnger').get_text().strip()
            else:
                type = 'article'
                date = soup.find(class_='pr-promo-date-time').get_text()
                title = soup.find(class_='title-wrap').get_text()
                text = soup.find(class_='text').find_all('p')
                content = ''
                for p in text:
                    content += p.get_text().strip() + ' '
        elif url.count('space.com') > 0:
            article = soup.find(class_='news-article')
            type = 'article'
            title = article.find('header').get_text().strip()
            date = article.find('time').get_text().strip()
            text = article.find(id='article-body').find_all('p')
            content = ''
            for p in text:
                content += p.get_text().strip() + ' '
        elif url.count('/books/') > 0:
            date = '*'
            article = soup.find(class_='document')
            title = article.find(class_='title').get_text().strip()
            content = ''
            text = article.find_all('p')
            for p in text:
                content += p.get_text().strip() + ' '
            type = 'book'

        p_title = self.parse_string(title)
        p_content = self.parse_string(content)
        for i in p_title:
            self.add_to_index(i, doc_id)
        for i in p_content:
            self.add_to_index(i, doc_id, False)
        if len(content) > 800:
            content = content[:800] + '...'
        self.store_doc(doc_id, url, type, title, content, date)
        self.scraped.append(url)
        Indexer.save_obj(self.scraped, 'scraped')

    def store_doc(self, doc_id, url, type, title, summary, date):
        if Document.objects.filter(url=url).exists():
            return False
        D = Document()
        D.docID = doc_id
        D.url = url
        D.type = type
        D.title = title
        D.summary = summary
        D.date = date
        D.save()
        self.num_docs += 1
        return True

    def index_google_results(self, results):
        doc_id = self.num_docs
        for res in results:
            for r in res:
                title = r.title
                url = r.link
                content = r.snippet
                type = 'misc'
                date = '*'
                p_title = self.parse_string(title)
                p_content = self.parse_string(content)

                for i in p_title:
                    self.add_to_index(i, doc_id)
                for i in p_content:
                    self.add_to_index(i, doc_id, False)

                if len(content) > 800:
                    content = content[:800] + '...'
                self.store_doc(doc_id, url, type, title, content, date)
                doc_id += 1

    @staticmethod
    def save_obj(obj, name):
        with open('obj/' + name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load_obj(name):
        with open('Index/obj/' + name + '.pkl', 'rb') as f:
            return pickle.load(f)
