#!/usr/bin/env python3

import json
import requests
from bs4 import BeautifulSoup
import re

def find_text_and_link(url):
    page = requests.get(url)
    content = page.content
    soup = BeautifulSoup(content, 'html.parser')
    # generate file name excluding a unspecify symbols
    regex = re.sub(r'[\[\]\',:\/\\\.-]', '&', url)
    name = ''.join([regex, '.json'])
    jsonfile = open(name, "w")
    for href in soup.find_all('a'):
        print(json.dumps({"text": str(href), "link": str(href.get('href'))}), file=jsonfile)
    jsonfile.close()

if __name__ == "__main__":
    find_text_and_link("http://www.google.com")
    find_text_and_link("https://www.sarov.info")
