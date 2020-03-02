
import requests
import re
import urllib

from tortoises.agent import get_headers
from tortoises.thread import ProcessWrapper


PDF_PATTERN = re.compile(r'(?:href|HREF)="?((?:http://)?.+?\.pdf)')


url = 'http://web.stanford.edu/class/cs106b/'
html = requests.get(url=url, headers=get_headers(random=True))

tasks = [url + _ for _ in PDF_PATTERN.findall(html.text)]


def download_pdf(pdf_url, path=''):

    file_name = pdf_url.split('/')[-1]
    r = urllib.request.urlopen(url)
    block_sz = 8192

    with open(path + file_name, 'wb') as f:
        while True:
            buffer = r.read(block_sz)
            if not buffer:
                break
            f.write(buffer)
    print(f'saving < {file_name} > to path < {path} >')


pw = ProcessWrapper(download_pdf, tasks, 10)
pw.run()
