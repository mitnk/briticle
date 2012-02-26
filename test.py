#encoding=UTF-8

import re
import unittest
from briticle import Briticle

_MAX_LENGTH = 80
def safe_repr(obj, short=False):
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if not short or len(result) < _MAX_LENGTH:
        return result
    return result[:_MAX_LENGTH] + ' [truncated]...'


OFF_SETS = 20
IMAGE_TAG = r'\[IMG\d{3}\]'


class TestBriticle(unittest.TestCase):

    def testFileList(self):
        file_list = (
            ("tests/article_tag.html", 2395),
            ("tests/amix.dk.html", 2261),
            ("tests/37signal_post.html", 2728),
            ("tests/lixiaolai.com1.html", 834),
            ("tests/thenextweb.com.html", 487),
            ("tests/github_project.html", 1273),
            ("tests/weebly.com.html", 2870),
            ("tests/div_without_attrs.html", 1004),
            ("tests/div_without_attrs2.html", 4447),
            ("tests/div_without_attrs3.html", 21185),
            ("tests/div_without_attrs4.html", 18748),
            ("tests/remove_comments.html", 78),
            ("tests/remove_widget_and_x_post.html", 78),
        )

        for f, count in file_list:
            br = Briticle()
            br.open(file_=f)
            # Replace multi-space into one
            c = re.sub(r'  +', ' ', br.content)
            # Replace all the 1. \n 2. IMAGE_TAG before testing
            c = re.sub(r'\n|%s' % IMAGE_TAG, '', c)
            # Different parsers (html.parser, html5lib, lxml) have differnet 
            # methods dealing with space Not making the exactly same results
            self.assertAlmostEqual(len(c), count, delta=10)
            self.assertTrue(len(br.content_html) > len(br.content))
    
    def testTitle(self):
        br = Briticle()
        br.open(file_="./tests/mitnk.com2.html")
        self.assertEqual(br.title, u'KISS\u539f\u5219')

    def testFontSize(self):
        br = Briticle()
        br.open(file_="./tests/div_without_attrs4.html")
        self.assertTrue("font size=" not in br.content_html)

    def assertAlmostEqual(self, first, second, places=None, msg=None, delta=None):
        """
        Port from Python 2.7.1
        Fail if the two objects are unequal as determined by their
           difference rounded to the given number of decimal places
           (default 7) and comparing to zero, or by comparing that the
           between the two objects is more than the given delta.

           Note that decimal places (from zero) are usually not the same
           as significant digits (measured from the most signficant digit).

           If the two objects compare equal then they will automatically
           compare almost equal.
        """
        if first == second:
            # shortcut
            return
        if delta is not None and places is not None:
            raise TypeError("specify delta or places not both")

        if delta is not None:
            if abs(first - second) <= delta:
                return

            standardMsg = '%s != %s within %s delta' % (safe_repr(first),
                                                        safe_repr(second),
                                                        safe_repr(delta))
        else:
            if places is None:
                places = 7

            if round(abs(second-first), places) == 0:
                return

            standardMsg = '%s != %s within %r places' % (safe_repr(first),
                                                          safe_repr(second),
                                                          places)
        msg = self._formatMessage(msg, standardMsg)
        raise self.failureException(msg)

if __name__ == "__main__":
    unittest.main()
