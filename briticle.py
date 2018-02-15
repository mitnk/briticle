"""
Briticle

Extract the main content of a webpage.

Basic Usage:

>>> bs = Briticle()
>>> bs.open('http://example.com/blog-post-url/')
>>> print(bs.html) # the main content with html tags
>>> print(bs.text) # the main content

Author:
mitnk @ twitter
w@mitnk.com
"""

from html.parser import HTMLParser

import logging
import os
import re
import subprocess

from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import build_opener

try:
    import lxml
    has_lxml = True
except:
    has_lxml = False

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

opener = build_opener()
opener.addheaders = HEADERS


def download_to_local(url, local_path):
    r = opener.open(url, timeout=30)
    f = open(local_path, 'wb')
    f.write(r.read())
    f.close()

class Briticle:
    url = ''
    title = ''
    html = ''
    text = ''
    __text = None
    _removal_patterns = ['post-bottom-area', 'entryDescription',
        'toolsListContainer', 'BlogEntryInfo', 'related', 'meta', 'links',
        'sharing-', 'addthis_toolbox', 'post_header', 'comment', 'widget-']

    def _get_text(self):
        try:
            bs = BeautifulSoup(self.html, 'html.parser')
        except:
            return ''
        text = self._parse_raw_text(bs.get_text())
        return text

    @property
    def text(self):
        if not self.__text:
            self.__text = self._get_text()
        return self.__text

    def __init__(self, url=''):
        self.url = url
        if url:
            self.open(url)

    def is_empty(self):
        return len(self.html) < MIN_LIMIT

    def _parse_raw_text(self, txt):
        html_parser = HTMLParser()
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
            self.html = '{}'.format(tag)
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
                self.html = '{}'.format(max_tag)
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
            self.html = '{}'.format(tag)
            logging.debug(" *** Found it with algorithm !!! ***")
            return True
        return False

    def _get_content(self):
        # Stop searching if any of these methods return True
        logging.debug('Begin getting content...')
        self._search_with_article_tag() or \
        self._search_with_div_class() or \
        self._search_with_algorithm()
        if len(self.text) < MIN_LIMIT:
            self.__text = ""
            self.html = ""

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
        if 'posterous.com' in self.url:
            self._removal_patterns += ['editbox']

        if 'wiki' in self.url:
            self._removal_patterns += ['infobox', 'toc', 'siteSub', 'metadata',
                'editsection', 'jump-to-nav', 'printfooter']

            for tag in self.soup.find_all('a'):
                if 'href' in tag.attrs and tag['href'].endswith('.svg') and tag.img:
                    tag.replace_with(tag.img)
            for tag in self.soup.find_all('img'):
                if 'src' in tag.attrs and tag['src'].endswith('magnify-clip.png'):
                    tag.extract()

            for tag in self.soup.find_all('h2'):
                if 'See also' in tag.get_text():
                    for sibling in tag.find_next_siblings(True):
                        sibling.extract()
                    tag.extract()

    def _get_soup(self, url='', file_='', timeout=30):
        if file_:
            page = open(file_)
        else:
            page = opener.open(self.url, timeout=timeout)
        if has_lxml:
            self.soup = BeautifulSoup(page, 'lxml', from_encoding='utf8')
        else:
            self.soup = BeautifulSoup(page, 'html.parser', from_encoding='utf8')

    def _remove_useless_tags(self):
        soup = self.soup

        for tag in soup.find_all("font"):
            tag.attrs = {}

        for tag_name in ("p", "h1", "h2", "h3", "h4", "h5", "h6", "div", "span"):
            for tag in soup.find_all(tag_name):
                for key in list(tag.attrs.keys()):
                    del tag[key]

        for tag in soup.find_all('img'):
            if not tag.has_attr('src') or '//' in tag['src']:
                tag.decompose()
            else:
                new_tag = soup.new_tag('img', src=tag['src'])
                tag.replace_with(new_tag)

        for tag in soup.find_all('a'):
            if not tag.string:
                tag.decompose()
            elif not tag.has_attr('href') or not tag['href'].startswith('http'):
                new_tag = soup.new_tag('u')
                new_tag.string = tag.string
                tag.replace_with(new_tag)
            else:
                new_tag = soup.new_tag('a', href=tag['href'])
                new_tag.string = tag.string
                tag.replace_with(new_tag)
        for tag_name in ("abbr", "iframe", "input", "nav", "form", "script",
                "like", "plusone", "header", "fb:like", "g:plusone", "spanre",
                "noscript", "link", "button", "label", "data", "select",
                "textarea"):
            for tag in soup.find_all(tag_name):
                tag.decompose()

    def _remove_comment_js_css(self):
        for c in self.soup.find_all(text=lambda t:isinstance(t, Comment)):
            c.extract()
        for style in self.soup.find_all("style"):
            style.extract()
        for style in self.soup.find_all("script"):
            style.extract()

    def _get_title(self):
        title_tag = self.soup.html.title if hasattr(self.soup.html, "title") else None
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
            #TODO: extact out as an function
            elif src.startswith('../'):
                src_ = src
                url_ = re.sub(r'%s$' % self.url.strip('/').split('/')[-1], '', self.url.strip('/'))
                while src_.startswith('../'):
                    url_ = re.sub(r'%s$' % url_.strip('/').split('/')[-1], '', url_.strip('/'))
                    src_ = re.sub(r'^../', '', src_)
                src = url_ + src_
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
        p_meta = re.compile('|'.join(self._removal_patterns))
        for tag in self.soup.find_all(attrs=p_meta):
            tag.extract()
        for tag in self.soup.find_all(attrs={'id': p_meta}):
            tag.extract()


class BriticleException(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __unicode__(self):
        return u"BriticleException: %s" % self.reason

    def __str__(self):
        return "BriticleException: %s" % self.reason


class BriticleFile(Briticle):
    save_dir = ""
    html_file = ""
    txt_file = ""

    def __init__(self, url, save_dir):
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        self.url = url
        if url:
            self.open(url)

    def _get_file_name_from_title(self):
        if self.title:
            return re.sub(r'[^-\w ]+', '', self.title).replace(' ', '_')
        return ""

    def save_to_mobi(self, title="", file_name="", sent_by=""):
        if self.is_empty():
            raise BriticleException("File is empty")
        self.save_to_html(title, file_name)
        if not self.html_file or not os.path.exists(self.html_file):
            raise BriticleException("html version file does not exist while generating mobi")

        html = u'<html><head><meta http-equiv="content-type" content="text/html; charset=utf-8">'
        html += u'<title>%s</title></head><body>' % self.title
        with open(self.html_file) as f:
            content = f.read()
            for tag in ("h1", "h2", "h3", "h4"):
                content = re.sub(r'<%s [^>]*>' % tag, '<%s>' % tag, content)
            content = content.replace('<h2>', '<h3>').replace('<h1>', '<h2>')
            content = content.replace('</h2>', '</h3>').replace('</h1>', '</h2>')
            html += content
        if sent_by:
            html += u'Sent by %s' % sent_by
        html += u'</body></html>'
        html_file_temp = re.sub(r'\.html$', '.tmp.html', self.html_file)
        with open(html_file_temp, 'w') as f:
            f.write(html)
        nut_mobi_name = re.sub(r'.html$', '.mobi', (self.html_file.split('/')[-1]))
        cmd = ["/usr/local/bin/kindlegen", html_file_temp, "-o", nut_mobi_name]
        try:
            subprocess.check_output(cmd)
        except subprocess.CalledProcessError:
            # kindlegen will raise exit code 1 for warnning generatings
            # at this time mobi file was generated
            pass
        if os.path.exists(html_file_temp):
            os.remove(html_file_temp)
        mobi_file = re.sub(r'\.html$', '.mobi', self.html_file)
        if not os.path.exists(mobi_file):
            raise BriticleException("Failed generating mobi file")
        self.mobi_file = mobi_file
        return mobi_file

    def save_to_html(self, title="", file_name=""):
        """
        title: The <H1> title in the mobi file
        file_name: Save file as <file_name>.mobi
        """
        if self.is_empty():
            raise BriticleException("File is empty")
        if not title:
            title = self.title
        # Generate file name via title if doesn't exist
        if not file_name:
            if title:
                file_name = re.sub(r'[^-\w ]+', '', title).replace(' ', '_')
            else:
                file_name = re.sub(r'[^-\w ]+', '', self.title).replace(' ', '_')
            if not file_name:
                file_name = "Untitled_Documentation"

        # Save images to local and change the <img> src to new location
        i = 1
        soup = BeautifulSoup(self.html, 'html.parser')
        images = soup.find_all('img')
        for img in images:
            if 'src' not in img.attrs:
                continue
            src = img['src']
            image_ext = src.split(".")[-1]
            # Set it as PNG when suffix does not exist
            if len(image_ext) >= 5:
                image_ext = "png"
            image_name = "%03d.%s" % (i, image_ext)
            dir_image = os.path.join(self.save_dir, file_name)
            if not os.path.exists(dir_image):
                os.mkdir(dir_image)
            local_file_name = os.path.join(dir_image, image_name)
            try:
                download_to_local(src, local_file_name)
            except URLError:
                continue
            except Exception as e:
                if 'timed out' in str(e):
                    continue
                raise

            new_tag = soup.new_tag("img", src=file_name + "/" + image_name)
            img.replace_with(new_tag)
            i += 1

        html_file = os.path.join(self.save_dir, file_name + '.html')
        tags_h1 = soup.find_all('h1')
        h1_exists = True if (tags_h1 and len(tags_h1) == 1) else False
        with open(html_file, 'w') as f:
            html = u""
            if h1_exists:
                hr = soup.new_tag('hr')
                tags_h1[0].insert_after(hr)
            else:
                html = u'<h1>{}</h1>\r\n<hr/>\r\n'.format(title)
            html += '{}'.format(soup)

            # FIXME: netloc not correct for URLs ends with "xxx.com.cn"
            try:
                netloc = urlparse(self.url).netloc
                netloc = u".".join(netloc.split(".")[-2:])
            except:
                netloc = u"Original URL"
            html += u'<br/>From <a href="%s">%s</a>. ' % (self.url, netloc)
            f.write(html)
        self.html_file = html_file
        return html_file

    def save_to_txt(self, file_name):
        file_path = os.path.join(self.save_dir, file_name + '.txt')
        with open(file_path, 'w') as f:
            f.write(self.text)
            f.write(u"\n\n" + '{}'.format(self.url))
        return file_path
