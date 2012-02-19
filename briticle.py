"""
Briticle

Fetch Blog Articles via URLs

Author:
mitnk @ twitter
whgking@gmail.com
"""

import HTMLParser
import re
import urllib2

from BeautifulSoup import BeautifulSoup, Comment

class Briticle:
    def __init__(self, url=''):
        self.url = url
        if url:
            self.open(url)

    def _get_content(self):
        html_parser = HTMLParser.HTMLParser()
        content = ""
        for kls in CONTENT_CLASSES:
            if '-' in kls or len(kls) >= 8:
                tags = self.soup.findAll("div", {"class": re.compile(kls)})
            else:
                tags = self.soup.findAll("div", {"class": kls})
            if not tags:
                continue

            length = 0
            max_tag = None
            for tag in tags:
                text = ''.join(tag.findAll(text=True))
                if len(text) > length:
                    length = len(text)
                    max_tag = tag

            text = ''.join(max_tag.findAll(text=True))
            text = re.sub(r'\r*\n+', '\r\n\r\n', text)
            content = html_parser.unescape(text)
            if len(content) > MIN_LIMIT: # content is too short
                break

        if len(content) < MIN_LIMIT:
            for kls in CONTENT_IDS:
                tag = self.soup.find("div", {"id": kls})
                if tag:
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
            tag.replaceWith("\n" + IMAGE_TAG + "\n")

    def _deal_with_pre_code(self):
        for tag in self.soup.findAll('pre'):
            pass

    def _remove_meta_info(self):
        META_CLASSES = (
            "post-bottom-area",
            "wp-caption", # wordpress images
            "entryDescription", # wired.com
            "BlogEntryInfo",
            "post-meta",
            "footnotes",
            "addthis_toolbox",
            "widget-area",
            "sharing-",
            "author",
            "related_articles",
        )

        META_IDS = (
            "commentArea",
            "commentText",
        )

        for kls in META_CLASSES:
            for tag in self.soup.findAll("div", {"class": re.compile(kls)}):
                tag.extract()
        for kls in META_IDS:
            for tag in self.soup.findAll("div", {"id": kls}):
                tag.extract()

MIN_LIMIT = 50
IMAGE_TAG = "[Image]"
CONTENT_CLASSES = (
    "content",
    "entry-content", # wordpress
    "highlightText", # only for kindle share
    "article-body", # thenextweb.com
    "BlogText",
    "articleContent",
    "entry-body",
    "entrybody",
    "postBody", # http://news.cnet.com
    "post-body", # blogspot
    "blog-body", # economist.com/blogs
    "article_inner",
    "articleBody",
    "articlePage", # for wsj.com
    "storycontent",
    "storyText",
    "blogbody",
    "realpost",
    "asset-body",
    "entry",
    "article",
    "story", # techdirt.com
    "main",
    "text",
)

CONTENT_IDS = (
    "readme",
    "story",
    "-content", # need before 'post'
    "entry-",
    "post-",
    "post",
    "entry",
)
