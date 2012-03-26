"""
Briticle

Extract the main content of a webpage.

Basic Usage:

>>> bs = Briticle()
>>> bs.open('http://example.com/blog-post-url/')
>>> print bs.text # the main content
>>> print bs.html # the main content with html tags

Author:
mitnk @ twitter
whgking@gmail.com
"""

import HTMLParser
import logging
import os
import os.path
import re
import subprocess
import urllib2
from urlparse import urlparse

from bs4 import BeautifulSoup
from bs4.element import Comment


__all__ = ['Briticle']

VERSION = (1, 0, 0, 'rc', 1)

VERBOSE = False
MIN_LIMIT = 512

USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:10.0.2)"
    " Gecko/20100101 Firefox/10.0.2")
ACCEPT = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
HEADERS = [('User-agent', USER_AGENT), ("Accept", ACCEPT)]

def download_to_local(url, local_name):
    opener = urllib2.build_opener()
    opener.addheaders = HEADERS
    r = opener.open(url, timeout=9)
    f = open(local_name, 'wb')
    f.write(r.read())
    f.close()

class Briticle:
    def __init__(self, url=''):
        self.url = url
        self.title = ""
        self.text = self.html = ""
        if url:
            self.open(url)

    def is_empty(self):
        return len(self.text) < MIN_LIMIT or len(self.html) < MIN_LIMIT

    def _parse_raw_text(self, txt):
        html_parser = HTMLParser.HTMLParser()
        txt = re.sub(r'\t', '', txt)
        txt = re.sub(r'\r', '', txt)
        txt = re.sub(r'\n+', '\n\n', txt)
        return html_parser.unescape(txt)

    def _search_with_article_tag(self):
        """ Using HTML5 <article> tag 

        Only works well with html5lib or lxml
        """
        tag = self.soup.article
        if tag:
            self.text = self._parse_raw_text(tag.get_text())
            self.html = unicode(tag)
            logging.debug(" *** Found it with article tag !!! ***")
            return True
        return False

    def _search_with_div_class(self):
        """ Get content with <div> class names """
        CONTENT_CLASSES = ( "entry-content", "article-body", "body-copy",
            "-post", "BlogText", "articleContent", "entrybody", "postBody",
            'blogbody', "article_inner", "articleBody", "realpost",
            "article", "story", "entry")
        for kls in CONTENT_CLASSES:
            logging.debug("searching div with class name: [%s] ..." % kls)
            if '-' in kls or len(kls) >= 8:
                tags = self.soup.find_all("div", {"class": re.compile(kls)})
            else:
                tags = self.soup.find_all("div", {"class": kls})
            if not tags:
                continue

            # find the div with Max content
            length = 0
            max_tag = None
            for tag in tags:
                text = tag.get_text()
                if len(text) > length:
                    length = len(text)
                    max_tag = tag

            content = self._parse_raw_text(max_tag.get_text())
            if len(content) > MIN_LIMIT:
                self.text = content
                self.html = unicode(max_tag)
                logging.debug(" *** Found it with DIV class !!! ***")
                return True
        return False
        
    def _search_with_algorithm(self):
        """ Try to find the main div tag with <p> inside """
        logging.debug("searching main div with algorithm ...")
        tag = self._search_divs_with_h1() or \
            self._search_p_biggest_parent() or \
            self._search_divs_with_p()
        if tag:
            # If tag contains body, assign it as body
            if tag.body:
                tag = tag.body
            # If tag is not div, rename it as DIV
            # This is for case tag.name is like <td>, which is invalid for kindlegen
            if tag.name != "div":
                tag.name = "div"
            self.text = self._parse_raw_text(tag.get_text())
            self.html = unicode(tag)
            logging.debug(" *** Found it with algorithm !!! ***")
            return True
        return False

    def _get_content(self):
        # Stop searching if any of these methods return True
        logging.debug('Begin getting content...')
        self._search_with_article_tag() or \
        self._search_with_div_class() or \
        self._search_with_algorithm()
        self.text = self.text
        if len(self.text) < MIN_LIMIT:
            self.text = self.html = ""

    def open(self, url="", file_=""):
        if url:
            self.url = url
        self._get_soup(url, file_)
        self._remove_comment_js_css()
        self._remove_useless_tags()
        self._deal_with_special_sites()
        self._get_title()
        self._deal_with_line_breaks()
        self._deal_with_images()
        self._remove_meta_info()
        self._get_content()

    def _deal_with_special_sites(self):
        if 'wiki' in self.url:
            for tag in self.soup.find_all('a'):
                if 'href' in tag.attrs and tag['href'].endswith('.svg') and tag.img:
                    tag.replace_with(tag.img)
            for tag in self.soup.find_all('img'):
                if 'src' in tag.attrs and tag['src'].endswith('magnify-clip.png'):
                    tag.extract()

            for tag in self.soup.findAll('h2'):
                if 'See also' in tag.get_text():
                    for sibling in tag.find_next_siblings(True):
                        sibling.extract()
                    tag.extract()
            p_meta = re.compile(r'infobox|toc|siteSub|metadata|editsection|jump-to-nav|printfooter')
            for tag in self.soup.find_all(attrs=p_meta):
                tag.extract()
            for tag in self.soup.find_all(attrs={'id': p_meta}):
                tag.extract()

    def _get_soup(self, url='', file_='', timeout=5):
        if file_:
            page = open(file_)
        else:
            opener = urllib2.build_opener()
            opener.addheaders = HEADERS
            page = opener.open(self.url, timeout=timeout)
        self.soup = BeautifulSoup(page, from_encoding='utf8')

    def _remove_useless_tags(self):
        for tag in self.soup.find_all("font"):
            tag.attrs = {}

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
        if not self.url:
            return

        for tag in self.soup.find_all('img'):
            if 'src' not in tag.attrs:
                continue
            src = tag['src']
            if src.startswith('//'):
                src = urlparse(self.url).scheme + ":" + src
            elif not src.startswith('http'):
                src = 'http://' + urlparse(self.url).netloc + "/" + src
            tag['src'] = src

    def _search_divs_with_h1(self):
        """
        Search all DIVs contain <h1>, return the biggest one.
        - If there are more such <DIV>s, and share one parent, return this parent.
        - Else, return the biggest <DIV>

        Return a Tag or None
        """
        logging.debug("searching div with h1 inside ...")
        div_with_h1 = None
        count_div_with_h1 = 0
        max_size = 0
        parents = []
        for tag in self.soup.find_all("div"):
            for child in tag.children:
                if hasattr(child, 'name') and child.name == "h1":
                    count_div_with_h1 += 1
                    if tag.parent not in parents:
                        parents.append(tag.parent)
                    size = len(tag.get_text())
                    if size > MIN_LIMIT and size > max_size:
                        max_size = size
                        div_with_h1 = tag
                    break
        if count_div_with_h1 > 1 and len(parents) == 1:
            return parents[0]
        elif div_with_h1:
            return div_with_h1

    def _search_p_biggest_parent(self):
        """
        Try to find main content with P tags
        if over 70% of P share with the same one parent, return the parent
        """
        logging.debug("searching P biggest parent ...")

        P_COUNT_LIMIT = 3
        PERCENT_LIMIT = 0.70
        tags = self.soup.find_all("p")
        if tags and len(tags) > P_COUNT_LIMIT:
            parents = []
            for p in tags:
                if not p.parents:
                    continue
                if p.parent not in parents:
                    parents.append(p.parent)
                else:
                    count = getattr(p.parent, 'count', 0) or 1
                    setattr(p.parent, 'count', count + 1)
            for tag in parents:
                if len(tag.get_text()) > MIN_LIMIT and \
                    int(getattr(tag, 'count', 0) or 1) >  len(tags) * PERCENT_LIMIT:
                    return tag

    def _search_divs_with_p(self):
        """
        Try to find the biggest DIV with p inside.
        """
        logging.debug("searching biggest div with p inside ...")

        tags = self.soup.find_all("div")
        if not tags:
            return None

        max_len = 0
        max_div = None
        for tag in tags:
            # Check if there are P tag inside, if not, not a main DIV
            has_p = False
            for child in tag.children:
                if hasattr(child, 'name') and child.name == "p":
                    has_p = True
                    break
            if not has_p:
                continue
            
            length = len(tag.get_text())
            if length > MIN_LIMIT and length > max_len:
                max_len = length
                max_div = tag
        return max_div

    def _remove_meta_info(self):
        """
        Remove all tags whose id or class attr with the following chars
        """
        p_meta = re.compile(r'post-bottom-area|entryDescription|'
            r'toolsListContainer|BlogEntryInfo|related|meta|sharing-|'
            r'addthis_toolbox|post_header|comment|widget-|links')
        for tag in self.soup.find_all(attrs=p_meta):
            tag.extract()
        for tag in self.soup.find_all(attrs={'id': p_meta}):
            tag.extract()

    def save_to_file(self, dir_name, title="", sent_by=None):
        if self.is_empty():
            return None

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

        # Save images to local and change the <img> src to new location
        i = 1
        soup = BeautifulSoup(self.html, 'html.parser')
        images = soup.findAll('img')
        for img in images:
            if 'src' not in img.attrs:
                continue
            src = img['src']
            image_ext = src.split(".")[-1]
            if len(image_ext) != 3:
                # Guess a ext when does not exist
                image_ext = "png"
            image_name = "%s_%s.%s" % (file_name, i, image_ext)
            local_file_name = os.path.join(dir_name, image_name)
            try:
                download_to_local(src, local_file_name)
            except urllib2.URLError:
                continue
            new_tag = soup.new_tag("img", src=image_name)
            img.replace_with(new_tag)
            i += 1
        self.html = unicode(soup)

        html_file = os.path.join(dir_name, file_name + '.html')
        with open(html_file, 'w') as f:
            html = u'<html><head><meta http-equiv="content-type" content="text/html; charset=utf-8">'
            if title:
                html += u'<title>%s</title></head><body><h1>%s</h1>' % (title, title)
            else:
                html += u'<title>%s</title></head><body><h1>%s</h1>' % (self.title, self.title)
            html += self.html
            try:
                netloc = urlparse(self.url).netloc
                netloc = u".".join(netloc.split(".")[-2:])
            except:
                netloc = u"Original URL"
            html += u'<br/>From <a href="%s">%s</a>. ' % (self.url, netloc)
            if sent_by:
                html += u'Sent by %s' % sent_by
            html += u'</body></html>'
            f.write(html.encode('utf-8'))
        mobi_file = _generate_mobi()
        _clean_temp_files()

        # Create a txt file if mobi file failed to generated
        if not mobi_file:
            txt_file = os.path.join(dir_name, file_name + '.txt')
            with open(txt_file, 'w') as f:
                f.write(self.text.encode('utf-8'))
                f.write(u"\n\n" + unicode(self.url))
            return txt_file
        return mobi_file


