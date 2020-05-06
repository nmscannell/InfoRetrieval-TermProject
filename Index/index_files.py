import sys
import os
import django

sys.path.append('/home/scannell/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'TRTerm.settings'
django.setup()

from Index.Indexer import Indexer


indexer = Indexer()
doc_id = 0
for i in range(1, 69):
    print(doc_id)
    indexer.process_file('files/' + str(i)+'.txt', doc_id)
    doc_id += 1

with open('urls.txt') as f:
    for line in f:
        print(doc_id)
        print(line)
        indexer.scrape_web(line.strip('\n'), doc_id)
        doc_id += 1

print(indexer.index)
for i in indexer.index:
    print(i)
