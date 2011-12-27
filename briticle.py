"""
Briticle

Fetch Blog Articles via URLs

Author:
mitnk [AT] twitter
whgking [AT] gmail [DOT] com
"""

import HTMLParser
import re
import urllib2
from BeautifulSoup import BeautifulSoup, Comment

class Briticle:
    def __init__(self, url=''):
        self.url = url

    def _get_content(self):
        html_parser = HTMLParser.HTMLParser()
        content = ""
        for kls in CONTENT_CLASSES:
            if len(kls) >= 8:
                tag = self.soup.find("div", {"class": re.compile(kls)})
            elif kls == "post":
                tag = self.soup.find("div", {"class": kls})
                if not tag:
                    tag = self.soup.find("div", {"class": re.compile(kls)})
            else:
                tag = self.soup.find("div", {"class": kls})
            if not tag:
                continue

            text = ''.join(tag.findAll(text=True))
            text = re.sub(r'\r*\n+', '\r\n\r\n', text)
            content = html_parser.unescape(text)
            if len(content) > MIN_LIMIT: # content is too short
                break

        if content < MIN_LIMIT:
            for kls in CONTENT_IDS:
                if '-' in kls:
                    tag = self.soup.find("div", {"id": re.compile(kls)})
                else:
                    tag = self.soup.find("div", {"id": kls})

                text = ''.join(tag.findAll(text=True))
                text = re.sub(r'\r*\n+', '\r\n\r\n', text)
                content = html_parser.unescape(text)

                if len(content) > MIN_LIMIT: # content is too short
                    break
        self.content = content

    def open(self, url="", file_=""):
        if url:
            self.url = url

        self._get_soup(url, file_)
        self._remove_comment_js_css()
        self._get_title()
        self._deal_with_line_breaks()
        self._deal_with_images()
        self._deal_with_pre_code()
        self._remove_meta_info()
        self._get_content()

    def _get_soup(self, url='', file_='', timeout=5):
        if file_:
            page = open(file_)
        else:
            page = urllib2.urlopen(self.url, timeout=timeout)

        try:
            self.soup = BeautifulSoup(page, fromEncoding='utf8')
        except UnicodeEncodeError:
            self.soup = BeautifulSoup(page, fromEncoding='gb18030')

    def _remove_comment_js_css(self):
        for c in self.soup.findAll(text=lambda t:isinstance(t, Comment)):
            c.extract()
        for style in self.soup.findAll("style"):
            style.extract()
        for style in self.soup.findAll("script"):
            style.extract()

    def _get_title(self):
        title_tag = self.soup.find("title")
        if title_tag:
            title = re.sub(r'[^a-zA-Z0-9_ -]+', '', self.soup.find("title").string)
            title = title.strip().replace('  ', ' ').replace(' ', '_')
        else:
            title = "No_Title_Found"
        self.title = title

    def _deal_with_line_breaks(self):
        for tag in self.soup.findAll('br'):
            tag.replaceWith("\n")

        for tag in self.soup.findAll('p'):
            tag.insert(0, "\n")

    def _deal_with_images(self):
        for tag in self.soup.findAll('img'):
            tag.replaceWith("\n[Image]\n")

    def _deal_with_pre_code(self):
        for tag in self.soup.findAll('pre'):
            pass

    def _remove_meta_info(self):
        META_CLASSES = (
            "post-bottom-area",
            "wp-caption", # wordpress images
            "entryDescription", # wired.com
            "post-meta",
            "footnotes",
            "addthis_toolbox",
            "widget-area",
            "sharing-",
            "author",
            "related_articles",
        )

        for kls in META_CLASSES:
            for tag in self.soup.findAll("div", {"class": re.compile(kls)}):
                tag.extract()

MIN_LIMIT = 50
CONTENT_CLASSES = (
    "entry-content", # wordpress
    "highlightText", # only for kindle share
    "articleContent",
    "entry-body",
    "entrybody",
    "KonaBody", # thenextweb.com
    "postBody", # http://news.cnet.com
    "post-body", # blogspot
    "blog-body", # economist.com/blogs
    "article_inner",
    "articleBody",
    "articlePage", # for wsj.com
    "storycontent",
    "the-content",
    "storyText",
    "blogbody",
    "realpost",
    "asset-body",
    "entry",
    "article",
    "-content",
    "post",
    "copy",
    "story", # techdirt.com
    "text",
    "main",
)

CONTENT_IDS = (
    "story",
    "-content", # need before 'post'
    "entry-",
    "post-",
    "post",
    "entry",
)
