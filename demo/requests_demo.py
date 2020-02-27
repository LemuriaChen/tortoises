
import requests


# 使用 requests 发送请求
# get 请求
r = requests.get('https://api.github.com/events')
print(r.json())

# post 请求
r = requests.post('http://httpbin.org/post', data={'key': 'value'})
print(r.json())

# put 请求
r = requests.put('http://httpbin.org/put', data = {'key':'value'})
print(r.json())

# delete 请求
r = requests.delete('http://httpbin.org/delete')
print(r.json())

# head 请求
r = requests.head('http://httpbin.org/get')
print(r.headers)

# options 请求
r = requests.options('http://httpbin.org/get')
print(r.headers)

# 传递 URL 参数
# 传递字典参数
payload = {'key1': 'value1', 'key2': 'value2'}
r = requests.get("http://httpbin.org/get", params=payload)
print(r.url)

# 传递字典参数（值可以为列表）
payload = {'key1': 'value1', 'key2': ['value2', 'value3']}
r = requests.get('http://httpbin.org/get', params=payload)
print(r.url)

# 响应内容
"""
请求发出后，Requests 会基于 HTTP 头部对响应的编码作出有根据的推测。
当你访问 r.text 之时，Requests 会使用其推测的文本编码。
你可以找出 Requests 使用了什么编码，并且能够使用 r.encoding 属性来改变它
"""
r = requests.get('https://api.github.com/events')
print(r.text)

# 定制请求头
"""
注意: 定制 header 的优先级低于某些特定的信息源，例如：
    如果在 .netrc 中设置了用户认证信息，使用 headers= 设置的授权就不会生效。而如果设置了 auth= 参数，``.netrc`` 的设置就无效了。
    如果被重定向到别的主机，授权 header 就会被删除。
    代理授权 header 会被 URL 中提供的代理身份覆盖掉。
    在我们能判断内容长度的情况下，header 的 Content-Length 会被改写。
"""
url = 'https://api.github.com/some/endpoint'
headers = {'user-agent': 'my-app/0.0.1'}
r = requests.get(url, headers=headers)
print(r.headers)

# Cookie
# 如果某个响应中包含一些 cookie，你可以快速访问它们
url = 'http://example.com/some/cookie/setting/url'
r = requests.get(url)
print(r.cookies)

# 要想发送你的cookies到服务器，可以使用 cookies 参数：
url = 'http://httpbin.org/cookies'
cookies = dict(cookies_are='working')
r = requests.get(url, cookies=cookies)
print(r.text)


# 抓取网站 / app

# 微博
# 知乎
# QQ邮箱




