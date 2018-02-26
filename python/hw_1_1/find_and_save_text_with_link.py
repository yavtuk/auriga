#!/usr/bin/env python3

import json
import requests
from bs4 import BeautifulSoup
import re

def get_page_content(url):
    page = requests.get(url)
    content = page.content
    soup = BeautifulSoup(content, 'html.parser')
    return soup


def create_name_from_url(url):
    # generate file name excluding a unspecify symbols
    regex = re.sub(r'[\[\]\',:\/\\\.-]', '&', url)
    name = ''.join([regex, '.json'])
    return name


def save_to_json_file(data, name):
    jsonfile = open(name, "w")
    print(data, file=jsonfile)
    jsonfile.close()


def find_text_and_link(page):
    data = ''
    for href in page.find_all('a'):
        data += json.dumps({"text": str(href), "link": str(href.get('href'))})
        data = ''.join([data, '\n'])
    return data


def find_and_save_text_with_link(url):
    content = get_page_content(url)
    data = find_text_and_link(content)
    name = create_name_from_url(url)
    save_to_json_file(data, name)


if __name__ == "__main__":
    find_and_save_text_with_link("http://www.google.com")
    find_and_save_text_with_link("https://www.auriga.com")
