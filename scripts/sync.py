#!/usr/bin/env python3
#coding: utf8

import os
from functools import reduce, partial


import urllib.request
import urllib.parse
import html.parser

URL_BASE = "https://resources.publicense.moe.edu.tw"


class MyHTMLParser(html.parser.HTMLParser):
    def __init__(self):
        self.links = []
        super().__init__()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for (key, value) in attrs:
                if key == "href":
                    if value.startswith("download/dict_"):
                        link = urllib.parse.urljoin(URL_BASE, value)
                        self.links.append(link)

def find_links(url):
    req = urllib.request.urlopen(url)
    text = req.read().decode("utf8")

    parser = MyHTMLParser()
    parser.feed(text)

    
    urls = []
    for link in parser.links:
        if "/dict_concised_music_" in link:
            # 排除多媒体资料
            print("[WARN] 忽略下载该文件: %s" % link)
        else:
            urls.append(link)

    return urls

def main():
    urls = [
        # 《重編國語辭典修訂本》資料下載
        "https://resources.publicense.moe.edu.tw/dict_reviseddict_download.html",
        # 《國語辭典簡編本》資料下載
        "https://resources.publicense.moe.edu.tw/dict_concised_download.html",
        # 《國語小字典》資料下載
        "https://resources.publicense.moe.edu.tw/dict_mini_download.html",
        # 《成語典》
        "https://resources.publicense.moe.edu.tw/dict_idiomsdict_download.html",
    ]

    items = reduce(lambda acc, url: acc + find_links(url), urls, [])

    for url in items:
        # Download
        cmd = "aria2c -d ./download -c \"%s\"" % url
        print(cmd)
        os.system(cmd)

    # Unzip
    os.chdir("./download/")
    for filename in os.listdir("./"):
        if filename.endswith(".zip"):
            # NOTE: macOS 系统的 unzip 以及 7z 软件无法支持 非系统默认编码的输入 参数。
            #       所以这里我们使用 unar.
            #       通过 `brew install unar` 获得。
            cmd = "unar -e big5 -f -output-directory \"../data/\" %s" % filename
            print(cmd)
            os.system(cmd)

if __name__ == '__main__':
    main()