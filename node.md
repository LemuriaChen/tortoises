
# python 爬虫常用库

## 请求库：实现 HTTP 请求操作

* urllib：一系列用于操作URL的功能。
* requests：基于 urllib 编写的，阻塞式 HTTP 请求库，发出一个请求，一直等待服务器响应后，程序才能进行下一步处理。
* selenium：自动化测试工具。一个调用浏览器的 driver，通过这个库你可以直接调用浏览器完成某些操作，比如输入验证码。
* aiohttp：基于 asyncio 实现的 HTTP 框架。异步操作借助于 async/await 关键字，使用异步库进行数据抓取，可以大大提高效率。

## 解析库：从网页中提取信息

* beautifulsoup：html 和 XML 的解析,从网页中提取信息，同时拥有强大的 API 和多样解析方式。
* pyquery：jQuery 的 Python 实现，能够以 jQuery 的语法来操作解析 HTML 文档，易用性和解析速度都很好。
* lxml：支持 HTML 和 XML 的解析，支持 XPath 解析方式，而且解析效率非常高。
* tesserocr：一个 OCR 库，在遇到验证码（图形验证码为主）的时候，可直接用 OCR 进行识别。

## 存储库：Python 与数据库交互

* pymysql：一个纯 Python 实现的 MySQL 客户端操作库。
* pymongo：一个用于直接连接 mongodb 数据库进行查询操作的库。
* redisdump：一个用于 redis 数据导入/导出的工具。基于 ruby 实现的，因此使用它，需要先安装 Ruby。

## 爬虫框架

* Scrapy：很强大的爬虫框架，可以满足简单的页面爬取（比如可以明确获知url pattern的情况）。
用这个框架可以轻松爬下来如亚马逊商品信息之类的数据。但是对于稍微复杂一点的页面，如 weibo 的页面信息，这个框架就满足不了需求了。
* Crawley：高速爬取对应网站的内容，支持关系和非关系数据库，数据可以导出为 JSON、XML 等。
* Portia：可视化爬取网页内容。
* newspaper：提取新闻、文章以及内容分析。
* python-goose：java 写的文章提取工具。
* cola：一个分布式爬虫框架。项目整体设计有点糟，模块间耦合度较高。

## Web 框架库

* flask：轻量级的 web 服务程序，简单，易用，灵活，主要来做一些 API 服务。做代理时可能会用到。
* django：一个 web 服务器框架，提供了一个完整的后台管理，引擎、接口等，使用它可做一个完整网站。

## 网页分析工具

* postman

## APP爬取相关库

* Charles 是一个网络抓包工具，相比 Fiddler，其功能更为强大 且跨平台支持得更好。
* mitmproxy 是一个支持HTTP和HTTPS的抓包工具，类似于Fiddler，Charles的功能，只不过它通过控制台的形式操作。

