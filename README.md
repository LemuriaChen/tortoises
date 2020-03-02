

# A web crawler for academic resources


## Installation

```shell script
pip install tortoises
```

## Features

### web of science

**usage**

* step 1

```shell script
# install google chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt install -f -y --fix-missing
sudo apt-get -f install -y

/usr/bin/google-chrome-stable --version

# install google chrome driver
wget https://npm.taobao.org/mirrors/chromedriver/80.0.3987.106/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/bin/

chromedriver --version
```
* step 2

```python
from tortoises.scholar import AppWebKnowledge

title = 'The ERA-Interim reanalysis: configuration and performance of the data assimilation system'
apk = AppWebKnowledge(headless=True)
apk.fetch_homepage(argument=title, mode='title')
apk.parse_article()

print(apk.parsed_info)
```

### pdf bulk downloader

### scholar 

