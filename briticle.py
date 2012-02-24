"""
Briticle

Fetch Blog Articles via URLs

Author:
mitnk @ twitter
whgking@gmail.com
"""

import HTMLParser
import os
import os.path
import re
import subprocess
import urllib
import urllib2
from urlparse import urlparse

from bs4 import BeautifulSoup
from bs4.element import Comment

VERBOSE = False


def print_info(info):
    if VERBOSE:
        print info

class Briticle:
    def __init__(self, url=''):
        self.content = self.content_html = ""
        self.images = {}
        self.url = url
        if url:
            self.open(url)

    def is_empty(self):
        return len(self.content) < MIN_LIMIT or len(self.content_html) < MIN_LIMIT

    def _parse_raw_text(self, txt):
        html_parser = HTMLParser.HTMLParser()
        txt = re.sub(r'\t', '', txt)
        txt = re.sub(r'\r', '', txt)
        txt = re.sub(r'\n+', '\n\n', txt)
        return html_parser.unescape(txt)

    def _search_article_tag(self):
        """ Using HTML5 <article> tag """
        tag = self.soup.article
        if tag:
            self.content = self._parse_raw_text(tag.get_text())
            self.content_html = unicode(tag)
            print_info(" *** Found it!!! ***")
            return True
        return False

    def _search_div_class(self):
        """ Get content with <div> class names """
        for kls in CONTENT_CLASSES:
            print_info("searching div with class name: [%s] ..." % kls)
            if '-' in kls or len(kls) >= 8:
                tags = self.soup.find_all("div", {"class": re.compile(kls)})
            else:
                tags = self.soup.find_all("div", {"class": kls})
            if not tags:
                continue

            length = 0
            max_tag = None
            for tag in tags:
                text = tag.get_text()
                if len(text) > length:
                    length = len(text)
                    max_tag = tag

            content = self._parse_raw_text(max_tag.get_text())
            if len(content) > MIN_LIMIT:
                self.content = content
                self.content_html = unicode(max_tag)
                print_info(" *** Found it!!! ***")
                return True
        return False
        
    def _search_div_id(self):
        """ Search tags with <div> IDs """
        for kls in CONTENT_IDS:
            print_info("searching div with ID name: [%s] ..." % kls)
            tag = self.soup.find("div", {"id": kls})
            if not tag:
                continue
            content = self._parse_raw_text(tag.get_text())
            if len(content) > MIN_LIMIT:
                self.content = content
                self.content_html = unicode(tag)
                print_info(" *** Found it!!! ***")
                return True
        return False

    def _search_main_div(self):
        """ Try to find the main div tag with <p> inside """
        print_info("searching main div without name ...")
        tag = self._search_main_tag()
        if tag:
            print_info(" *** Found it!!! ***")
            self.content_html = unicode(tag)
            self.content = self._parse_raw_text(tag.get_text())
            return True
        return False

    def _get_content(self):
        # Stop searching if any of these methods return True
        print_info('Begin getting content...')
        self._search_article_tag() or \
        self._search_div_class() or \
        self._search_div_id() or \
        self._search_main_div()
        if len(self.content) < MIN_LIMIT:
            self.content = self.content_html = ""

    def open(self, url="", file_=""):
        if url:
            self.url = url
        self._get_soup(url, file_)
        self._remove_comment_js_css()
        self._remove_useless_tags()
        self._get_title()
        self._deal_with_line_breaks()
        self._deal_with_images()
        self._remove_meta_info()
        self._get_content()

    def _get_soup(self, url='', file_='', timeout=5):
        if file_:
            page = open(file_)
        else:
            page = urllib2.urlopen(self.url, timeout=timeout)
        self.soup = BeautifulSoup(page, from_encoding='utf8')

    def _remove_useless_tags(self):
        for tag in self.soup.find_all("form"):
            tag.extract()

    def _remove_comment_js_css(self):
        for c in self.soup.find_all(text=lambda t:isinstance(t, Comment)):
            c.extract()
        for style in self.soup.find_all("style"):
            style.extract()
        for style in self.soup.find_all("script"):
            style.extract()

    def _get_title(self):
        title_tag = self.soup.html.title
        if title_tag:
            title = title_tag.string
        else:
            title = "No_Title_Found"
        self.title = title

    def _deal_with_line_breaks(self):
        for tag in self.soup.find_all('br'):
            tag.replace_with("\n")

        for tag in self.soup.find_all('p'):
            tag.insert(0, "\n")

    def _deal_with_images(self):
        i = 1
        for tag in self.soup.find_all('img'):
            if 'src' not in tag.attrs:
                continue
            name, src = "%03d" % i, tag['src']
            if not src.startswith('http') and self.url:
                src = 'http://' + urlparse(self.url).netloc + "/" + src
            self.images[name] = src
            tag.replace_with('\n[IMG' + name + ']\n')
            i += 1

    def _search_main_tag(self):
        ## Try to find H1 tag, whiose content should big enough (like over 1K)
        MAIN_CONTENT_LENGTH_LIMIT = 1000
        div_with_h1 = None
        count_div_with_h1 = 0
        max_size = 0
        parents_div_with_h1 = []
        for tag in self.soup.find_all("div"):
            for child in tag.children:
                if hasattr(child, 'name') and child.name == "h1":
                    count_div_with_h1 += 1
                    if tag.parent not in parents_div_with_h1:
                        parents_div_with_h1.append(tag.parent)
                    size = len(tag.get_text())
                    if size > max_size:
                        max_size = size
                        div_with_h1 = tag
                    break
        if count_div_with_h1 > 1 and len(parents_div_with_h1) == 1:
            return parents_div_with_h1[0]
        elif div_with_h1 and max_size > MAIN_CONTENT_LENGTH_LIMIT:
            return div_with_h1

        def find_max_div(tag_to_search):
            tags = tag_to_search.find_all("div")
            if not tags:
                if (not tag_to_search.find_all("p")) or \
                    (len(tag_to_search.get_text()) < MIN_LIMIT):
                    return tag_to_search.parent
                return tag_to_search

            max_count = 0
            max_div = None
            for tag in tags:
                text = tag.get_text()
                if len(text) > max_count:
                    max_count = len(text)
                    max_div = tag
            if not max_div:
                return tag_to_search
            return find_max_div(max_div)
            
        return find_max_div(self.soup)

    def _remove_meta_info(self):
        META_CLASSES = (
            "post-bottom-area",
            "wp-caption", # wordpress images
            "entryDescription", # wired.com
            "toolsListContainer",
            "BlogEntryInfo",
            "post-meta",
            "entry-meta",
            "entry-related",
            "addthis_toolbox",
            "widget-area",
            "sharing-",
            "related",
            "post_header",
            "comment",
            "comments",
            "widget-",
            "links",
        )

        META_IDS = (
            "commentArea",
            "commentText",
            "comment",
            "comments",
        )

        for kls in META_CLASSES:
            for tag in self.soup.find_all(attrs=re.compile(kls)):
                tag.extract()
        for kls in META_IDS:
            for tag in self.soup.find_all("div", {"id": kls}):
                tag.extract()

    def save_to_file(self, dir_name, title=""):
        assert(not self.is_empty())

        def _clean_temp_files():
            """ Remove images using in the html file """
            file_list = os.listdir(dir_name)
            for f in file_list:
                f = dir_name + "/" + f
                if os.path.isdir(f):
                    continue
                if not f.endswith(".mobi") and not f.endswith(".txt"):
                    os.remove(f)

        def _generate_mobi():
            nut_mobi_name = re.sub(r'.html$', '.mobi', (html_file.split('/')[-1]))
            cmd = ["kindlegen", html_file, "-o", nut_mobi_name]
            subprocess.call(cmd)
            mobi_file = re.sub(r'\.html$', '.mobi', html_file)
            if not os.path.exists(mobi_file):
                return None
            return mobi_file

        if title:
            file_name = re.sub(r'[^0-9a-zA-Z _-]+', '', title).replace(' ', '_')
        else:
            file_name = re.sub(r'[^0-9a-zA-Z _-]+', '', self.title).replace(' ', '_')
        if not file_name:
            file_name = "Untitled_Documentation"

        images = re.findall(r'\[IMG(\d{3})\]', self.content_html)
        for img_index in images:
            src = self.images[img_index]
            image_ext = src.split(".")[-1]
            if len(image_ext) != 3:
                continue
            image_name = "%s_%s.%s" % (file_name, img_index, image_ext)
            local_file_name = os.path.join(dir_name, image_name)
            urllib.urlretrieve(src, local_file_name)
            self.content_html = self.content_html.replace('[IMG%s]' % img_index, '<img src="%s">' % image_name)

        html_file = os.path.join(dir_name, file_name + '.html')
        with open(html_file, 'w') as f:
            html = '<html><head><meta http-equiv="content-type" content="text/html; charset=utf-8">'
            if title:
                html += '<title>%s</title></head><body><h1>%s</h1>' % (title, title)
            else:
                html += '<title>%s</title></head><body><h1>%s</h1>' % (self.title, self.title)
            html += self.content_html
            html += '<br/><a href="%s">Original URL</a>, Sent by mitnk.com</body></html>' % self.url
            f.write(html.encode('utf-8'))
        mobi_file = _generate_mobi()
        _clean_temp_files()

        # Create a txt file if mobi file failed to generated
        if not mobi_file:
            txt_file = os.path.join(dir_name, file_name + '.txt')
            with open(txt_file, 'w') as f:
                f.write(self.content.encode('utf-8'))
                f.write(u"\n\n" + unicode(self.url))
            return txt_file
        return mobi_file


MIN_LIMIT = 60
CONTENT_CLASSES = (
    "entry-content", # wordpress
    "highlightText", # only for kindle share
    "article-body", # thenextweb.com
    "body-copy", # techcrunch.com
    "-post",
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
