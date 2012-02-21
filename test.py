#encoding=UTF-8

import re
import unittest
from briticle import Briticle

OFF_SETS = 20
IMAGE_TAG = r'\[IMG\d{3}\]'


class TestBriticle(unittest.TestCase):

    def testFileList(self):
        file_list = (
            ("tests/article_tag.html", 2412),
            ("tests/amix.dk.html", 2294),
            ("tests/37signal_post.html", 2736),
            ("tests/lixiaolai.com1.html", 834),
            ("tests/thenextweb.com.html", 1450),
            ("tests/github_project.html", 1277),
            ("tests/petzl.com.html", 3721),
            ("tests/weebly.com.html", 2872),
            ("tests/div_without_attrs.html", 1115),
            ("tests/div_without_attrs2.html", 4525),
            ("tests/div_without_attrs3.html", 21297),
            ("tests/remove_comments.html", 78),
            ("tests/remove_widget_and_x_post.html", 78),
        )

        for f, count in file_list:
            br = Briticle()
            br.open(file_=f)
            c = re.sub(r'\n|%s' % IMAGE_TAG, '', br.content)
            self.assertEqual(len(c), count)
            self.assertTrue(len(br.content_html) > len(br.content))
    
    def testTitle(self):
        br = Briticle()
        br.open(file_="./tests/mitnk.com2.html")
        self.assertEqual(br.title, u'KISS\u539f\u5219')


if __name__ == "__main__":
    unittest.main()
