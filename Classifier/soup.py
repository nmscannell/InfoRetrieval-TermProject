import requests
from bs4 import BeautifulSoup
import csv
'''
URL = 'https://www.politifact.com/factchecks/2020/mar/31/facebook-posts/wisconsin-coronavirus-cases-peak-april-26-may-22/'
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')
section = soup.find(class_='m-textblock')
section = section.find_all('p')

print(section)
#results = section.get_text()
#print(results)'''

URL = "https://www.snopes.com/collections/new-coronavirus-collection/"
snopes = []
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')
section = soup.find(class_='card-body')
links = [a['href'] for a in section.find_all('a', href=True) if a['href'].count('collection') != 0]

for url in links:
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    section = soup.find(class_='collected-list col-12')
    for a in section.find_all('a', href=True):
        text = a.find(class_='media-body').get_text().strip()
        if text != 'False' and text != 'True':
            continue
        snopes.append(a['href'])

t_links = []
f_links = []
print('number of urls in snopes:' + str(len(snopes)))
for url in snopes:
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    rating = soup.find(class_='rating-wrapper card').find('h5').get_text().strip()
    print(rating)
    content = soup.find(class_='content-wrapper card').find(class_='content')
    p = content.find_all('p')
    i = 0
    while i < 2:
        section = p[i].find_all('a', href=True)
        if section is None:
            print('no links')
            continue
        for a in section:
            print(a['href'])
            if rating:
                t_links.append(a['href'])
            else:
                f_links.append(a['href'])
    print(len(t_links) + len(f_links))
    if len(t_links) + len(f_links) > 500:
        break

# store links in csv
with open('sources.csv', 'w') as csvf:
    writer = csv.writer(csvf)
    for i in t_links:
        writer.writerow(i + str(1))
    for i in f_links:
        writer.writerow(i + str(0))
