
import requests
import re
import os
from tortoises.agent import get_headers
from tortoises.thread import ProcessWrapper
import wget
import time
from urllib.error import HTTPError


PDF_PATTERN = re.compile(r'(?:href|HREF)="?((?:http://)?.+?\.pdf)')


url = 'http://web.stanford.edu/class/cs106b/'
html = requests.get(url=url, headers=get_headers(random=True))

tasks = list(set([url + _ for _ in PDF_PATTERN.findall(html.text)]))


def download_pdf(pdf_url, path='./'):
    print(pdf_url)
    try:
        file_name = pdf_url.split('/')[-1]
        wget.download(pdf_url, out=os.path.join(path, file_name))
    except HTTPError:
        pass


start = time.time()
pw = ProcessWrapper(download_pdf, tasks, 10)
pw.run()
end = time.time()
print(f'done, {round(end - start, 4)} seconds used.')
