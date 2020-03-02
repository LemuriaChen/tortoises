
import requests
from bs4 import BeautifulSoup

from tortoises.agent import get_headers


class Parser(object):
    def __init__(self, url):
        self.url = url


url = 'http://web.stanford.edu/class/cs106b/'

r = requests.get(url=url, headers=get_headers(random=True))

soup = BeautifulSoup(r.content, "html.parser")












