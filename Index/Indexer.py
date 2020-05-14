import requests
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')
from medsearch.models import Document
import pickle
import os.path
from bs4 import BeautifulSoup as bs

'''
Indexer parses and stores data in the database.
Data pulled from txt file or from web scraper.
All terms are lowercased, punctuation and stop words are removed.

Inverted index contains search terms with postings lists that contains term frequency for the 
title, term frequency for the content,  and source/type for each docID
Inverted index is stored in a dict that is saved and loaded via pickle.
'''


class Indexer:
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
            source = f.readline().strip('\n')
            title = f.readline().strip('\n')
            date = f.readline().strip('\n')
            content = ''
            for l in f.readlines():
                content += l.strip('\n').strip() + ' '
        p_title = self.parse_string(title)
        p_content = self.parse_string(content)

        prev = None
        for i in p_title:
            self.add_to_index(i, doc_id, source)
            if prev is not None:
                self.add_to_index(prev + ' ' + i, doc_id, source)
            prev = i

        prev = None
        for i in p_content:
            self.add_to_index(i, doc_id, source, False)
            if prev is not None:
                self.add_to_index(prev + ' ' + i, doc_id, source, False)
            prev = i

        self.store_doc(doc_id, url, source, title, content, date)

    def add_to_index(self, i, doc_id, source, title=True):
        if title:
            if i in self.index:
                if doc_id in self.index[i]:
                    if 'title' in self.index[i][doc_id]:
                        self.index[i][doc_id]['title'] = self.index[i][doc_id]['title'] + 1
                    else:
                        self.index[i][doc_id]['title'] = 1
                        self.index[i][doc_id]['type'] = source
                else:
                    self.index[i][doc_id] = {'title': 1, 'type': source}
            else:
                self.index[i] = {doc_id: {'title': 1, 'type': source}}
        else:
            if i in self.index:
                if doc_id in self.index[i]:
                    if 'body' in self.index[i][doc_id]:
                        self.index[i][doc_id]['body'] = self.index[i][doc_id]['body'] + 1
                    else:
                        self.index[i][doc_id]['body'] = 1
                        self.index[i][doc_id]['type'] = source
                else:
                    self.index[i][doc_id] = {'body': 1, 'type': source}
            else:
                self.index[i] = {doc_id: {'body': 1, 'type': source}}
        Indexer.save_obj(self.index, 'index')

    def parse_string(self, string):
        doc = string.split()
        tokens = []
        prev = None
        for i in range(len(doc)):
            doc[i] = doc[i].strip().strip('\u201C').strip('\u201D')
            if prev is None or prev.count('.') == 1:
                doc[i] = doc[i].lower()
            prev = doc[i]
            doc[i] = doc[i].strip('.\"\'!?,/\\*()-_&;~:[]{}')
            if len(doc[i]) == 0 or doc[i] in stopwords.words('english') or any(c.isdigit() for c in doc[i]) or doc[i] in self.punct:
                continue
            if doc[i].count('/') > 0 and doc[i].count('.com') == 0:
                words = doc[i].split('/')
                for j in range(len(words)):
                    tokens.append(words[j].strip('\u201C').strip('\u201D').strip('.\"\'!?,/\\*()-_&;~:[]{}'))
            elif doc[i].count('-') > 0 and doc[i].count('.com') == 0:
                words = doc[i].split('-')
                for j in range(len(words)):
                    tokens.append(words[j].strip('\u201C').strip('\u201D').strip('.\"\'!?,/\\*()-_&;~:[]{}'))
            elif doc[i].count('...') > 0:
                words = doc[i].split('...')
                for j in range(len(words)):
                    tokens.append(words[j].strip('\u201C').strip('\u201D').strip('.\"\'!?,/\\*()-_&;~:[]{}'))
            else:
                tokens.append(doc[i])
        return tokens

    def scrape_web(self, url, doc_id):
        if url in self.scraped:
            return
        page = requests.get(url)
        soup = bs(page.content, 'html.parser')
        content = ''
        if url.count('nasa.gov') > 0:
            if url.count('/experiments/') > 0:
                source = 'experiment'
                date = '*'
                title = soup.find(class_='inv-title').get_text().strip()
                content += soup.find(class_='block flagged').get_text().strip() + ' '
                content += soup.find(id='ResearchSummary').get_text().strip() + ' '
                content += soup.find(id='ResearchDescription').get_text().strip() + ' '
                content += soup.find(id='ApplicationsInSpaceAnger').get_text().strip()
            else:
                source = 'article'
                date = soup.find(class_='pr-promo-date-time').get_text()
                title = soup.find(class_='title-wrap').get_text()
                text = soup.find(class_='text').find_all('p')
                content = ''
                for p in text:
                    content += p.get_text().strip() + ' '
        elif url.count('space.com') > 0:
            article = soup.find(class_='news-article')
            source = 'article'
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
            source = 'book'

        p_title = self.parse_string(title)
        p_content = self.parse_string(content)
        prev = None
        for i in p_title:
            self.add_to_index(i, doc_id, source)
            if prev is not None:
                self.add_to_index(prev + ' ' + i, doc_id, source)
            prev = i

        prev = None
        for i in p_content:
            self.add_to_index(i, doc_id, source, False)
            if prev is not None:
                self.add_to_index(prev + ' ' + i, doc_id, source, False)
            prev = i

        self.store_doc(doc_id, url, source, title, content, date)
        self.scraped.append(url)
        Indexer.save_obj(self.scraped, 'scraped')

    def store_doc(self, doc_id, url, source, title, summary, date):
        if Document.objects.filter(url=url).exists():
            print('doc already in database: ' + doc_id)
            return False
        D = Document()
        D.docID = doc_id
        D.url = url
        D.type = source
        D.title = title
        D.summary = summary
        D.date = date
        D.save()
        self.num_docs += 1
        return True

    @staticmethod
    def save_obj(obj, name):
        with open('obj/' + name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load_obj(name):
        with open('Index/obj/' + name + '.pkl', 'rb') as f:
            return pickle.load(f)
