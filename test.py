#encoding=UTF-8

import re
import unittest
from briticle import Briticle

OFF_SETS = 20
IMAGE_TAG = r'\[IMG\d{3}\]'


class TestBriticle(unittest.TestCase):

    def testFileList(self):
        file_list = (
            ("tests/amix.dk.html", 2362),
            ("tests/37signal_post.html", 2831),
            ("tests/lixiaolai.com1.html", 875),
            ("tests/thenextweb.com.html", 1440),
            ("tests/github_project.html", 1317),
            ("tests/petzl.com.html", 3761),
            ("tests/weebly.com.html", 2899),
            ("tests/div_without_attrs.html", 1024),
        )

        for f, count in file_list:
            br = Briticle()
            br.open(file_=f)
            c = re.sub(r'\n|%s' % IMAGE_TAG, '', br.content)
            self.assertTrue(abs(len(c) - count) < OFF_SETS)
    
    def testTitle(self):
        br = Briticle()
        br.open(file_="./tests/mitnk.com2.html")
        self.assertEqual(br.title, u'KISS\u539f\u5219')


if __name__ == "__main__":
    unittest.main()
