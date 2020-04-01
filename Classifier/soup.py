import requests
from bs4 import BeautifulSoup

URL = 'https://www.politifact.com/factchecks/2020/mar/31/facebook-posts/wisconsin-coronavirus-cases-peak-april-26-may-22/'
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')
section = soup.find(class_='m-textblock')
section = section.find_all('p')

print(section)
#results = section.get_text()
#print(results)