"""
Briticle

Fetch Blog Articles via URLs

Author:
mitnk @ twitter
whgking@gmail.com
"""

import HTMLParser
import re
import urllib
import urllib2
from urlparse import urlparse

from BeautifulSoup import BeautifulSoup, Comment

VERBOSE = False


def print_info(info):
    if VERBOSE:
        print info

class Briticle:
    def __init__(self, url=''):
        self.images = {}
        self.url = url
        if url:
            self.open(url)

    def _get_content(self):
        html_parser = HTMLParser.HTMLParser()
        content = ""
        for kls in CONTENT_CLASSES:
            print_info("searching div with class name: [%s] ..." % kls)
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
            if len(content) > MIN_LIMIT:
                self.content_html = unicode(max_tag)
                print_info(" *** Found it!!! ***")
                break

        if len(content) < MIN_LIMIT:
            for kls in CONTENT_IDS:
                tag = self.soup.find("div", {"id": kls})
                print_info("searching div with id name: [%s] ..." % kls)
                if tag:
                    text = ''.join(tag.findAll(text=True))
                    text = re.sub(r'\r*\n+', '\r\n\r\n', text)
                    content = html_parser.unescape(text)
                    if len(content) > MIN_LIMIT:
                        self.content_html = unicode(tag)
                        print_info(" *** Found it!!! ***")
                        break
        
        if len(content) < MIN_LIMIT:
            print_info("searching main div without name ...")
            max_div = self._search_main_div()
            if max_div:
                print_info(" *** Found it!!! ***")
                self.content_html = unicode(max_div)
                content = ''.join(max_div.findAll(text=True))

        if len(content) < MIN_LIMIT:
            self.content = ""
        else:
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
        print_info('begin getting content...')
        self._get_content()

    def _get_soup(self, url='', file_='', timeout=5):
        if file_:
            page = open(file_)
        else:
            page = urllib2.urlopen(self.url, timeout=timeout)

        self.soup = BeautifulSoup(page, fromEncoding='utf8')

    def _remove_comment_js_css(self):
        for c in self.soup.findAll(text=lambda t:isinstance(t, Comment)):
            c.extract()
        for style in self.soup.findAll("style"):
            style.extract()
        for style in self.soup.findAll("script"):
            style.extract()

    def _get_title(self):
        title_tag = self.soup.html.title
        if title_tag:
            title = title_tag.string
        else:
            title = "No_Title_Found"
        self.title = title

    def _deal_with_line_breaks(self):
        for tag in self.soup.findAll('br'):
            tag.replaceWith("\n")

        for tag in self.soup.findAll('p'):
            tag.insert(0, "\n")

    def _deal_with_images(self):
        i = 1
        for tag in self.soup.findAll('img'):
            name, src = "%03d" % i, tag['src']
            if not src.startswith('http') and self.url:
                src = 'http://' + urlparse(self.url).netloc + "/" + src
            self.images[name] = src
            tag.replaceWith('\n[IMG' + name + ']\n')
            i += 1

    def _deal_with_pre_code(self):
        for tag in self.soup.findAll('pre'):
            pass

    def _search_main_div(self):
        def find_max_div(tag):
            tags = tag.findAll("div")
            if not tags:
                if not tag.findAll("p") or len(''.join(tag.findAll(text=True))) < MIN_LIMIT:
                    return tag.parent
                return tag

            max_count = 0
            max_div = None
            for tag in tags:
                text = ''.join(tag.findAll(text=True))
                if len(text) > max_count:
                    max_count = len(text)
                    max_div = tag
            return find_max_div(max_div)
            
        return find_max_div(self.soup)

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

    def _save_to_html(self, file_name, dir_name):
        if not self.content_html:
            raise Exception("No HTML content found.")

        images = re.findall(r'\[IMG(\d{3})\]', self.content_html)
        for img_index in images:
            src = self.images[img_index]
            image_ext = src.split(".")[-1]
            image_name = "%s%s.%s" % (file_name, img_index, image_ext)
            local_file_name = "%s/%s" % (dir_name, image_name)
            urllib.urlretrieve(src, local_file_name)
            self.content_html = self.content_html.replace('[IMG%s]' % img_index, '<img src="%s">' % image_name)

        with open(dir_name + "/" + file_name, 'w') as f:
            html = u'<html><head><meta http-equiv="content-type" content="text/html; charset=utf-8">'
            html += u'<title>%s</title></head><body>' % self.title
            html += self.content_html + '</body></html>'
            f.write(html.encode('utf-8'))


MIN_LIMIT = 50
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
    "post",
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
