#encoding=UTF-8

import os
import re
import unittest
from briticle import Briticle

OFF_SETS = 20
IMAGE_TAG = r'\[IMG\d{3}\]'


class TestBriticle(unittest.TestCase):

    def test_content_class(self):
        file_list = os.listdir('tests/content_class')
        for f in file_list:
            br = Briticle()
            br.open(file_='tests/content_class/' + f)
            self.assertTrue('bbbbb' not in br.text)
            self.assertOk(len(br.text.replace('\n', '')), 1400, delta=10)
            self.assertTrue(len(br.html) > len(br.text))


    def testFileList(self):
        file_list = (
            ("tests/article_tag.html", 2395),
            ("tests/amix.dk.html", 2261),
            ("tests/37signal_post.html", 2728),
            ("tests/thenextweb.com.html", 487),
            ("tests/github_project.html", 1273),
            ("tests/div_without_attrs.html", 1004),
            ("tests/div_without_attrs2.html", 4447),
            ("tests/bs4_doc.html", 5460),
            ("tests/div_without_attrs4.html", 18748),
            ("tests/div_without_attrs5.html", 4391),
            ("tests/div_without_attrs6.html", 2182),
            ("tests/remove_comments.html", 78),
            ("tests/remove_widget_and_x_post.html", 78),
        )

        for f, count in file_list:
            br = Briticle()
            br.open(file_=f)
            # Replace multi-space into one
            c = re.sub(r'  +', ' ', br.text)
            # Replace all the 1. \n 2. IMAGE_TAG before testing
            c = re.sub(r'\n|%s' % IMAGE_TAG, '', c)
            # Different parsers (html.parser, html5lib, lxml) have differnet 
            # methods dealing with space Not making the exactly same results
            self.assertOk(len(c), count, delta=10)
            self.assertTrue(len(br.html) > len(br.text))
    
    def testTitle(self):
        br = Briticle()
        br.open(file_="./tests/mitnk.com2.html")
        self.assertEqual(br.title, u'KISS\u539f\u5219')

    def testFontSize(self):
        br = Briticle()
        br.open(file_="./tests/div_without_attrs4.html")
        self.assertTrue("font size=" not in unicode(br.html))

    def testOthersToDiv(self):
        br = Briticle()
        br.open(file_="./tests/div_without_attrs6.html")
        self.assertTrue("<td>" not in br.html)
        br = Briticle()
        br.open(file_="./tests/div_without_attrs7.html")
        self.assertTrue("<body>" not in br.html)

    def assertOk(self, first, second, delta=None, msg=None):
        if first == second:
            return
        if delta is not None:
            if abs(first - second) <= delta:
                return
        standardMsg = '%s != %s within %s delta' % (first, second, delta)
        msg = self._formatMessage(msg, standardMsg)
        raise self.failureException(msg)

    def test_remove_meta_info(self):
        br = Briticle()
        br.open(file_="./tests/remove_meta_info.html")
        self.assertTrue("bbbb" not in br.text)
        self.assertTrue("bbbb" not in br.html)
        self.assertOk(len(br.text.replace('\n', '')), 700, delta=10)

if __name__ == "__main__":
    unittest.main()
