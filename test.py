import os
import re
import unittest
from briticle import Briticle


class TestBriticle(unittest.TestCase):

    def test_divs_class(self):
        file_list = os.listdir('tests/content_class')
        for f in file_list:
            br = Briticle()
            br.open(file_='tests/content_class/' + f)
            self.assertTrue('bbbbb' not in br.text)
            self.assertOk(len(br.text.replace('\n', '')), 1400, delta=10)
            self.assertTrue(len(br.html) > len(br.text))


    def test_special_sites(self):
        file_list = (
            ("tests/github_project.html", 1273),
            ("tests/bs4_doc.html", 5555),
            ("tests/wikipedia1.html", 29911),
            ("tests/wikipedia2.html", 1865),
        )

        for f, count in file_list:
            br = Briticle()
            br.open(file_=f)
            self.assertOk(len(br.text.replace('\n', '')), count, delta=10)
            self.assertTrue(len(br.html) > len(br.text))

    def test_title(self):
        br = Briticle()
        br.open(file_="./tests/functions/get_title1.html")
        self.assertEqual(br.title, u'KISS\u539f\u5219')
        br.open(file_="./tests/functions/get_title2.html")
        self.assertEqual(br.title, u'abc')

    def test_remove_font_size(self):
        br = Briticle()
        br.open(file_="./tests/functions/remove_font_size.html")
        self.assertTrue("font size=" not in '{}'.format(br.html))

    def test_always_return_div(self):
        br = Briticle()
        br.open(file_="./tests/functions/always_return_div1.html")
        self.assertTrue("<td>" not in br.html)
        br = Briticle()
        br.open(file_="./tests/functions/always_return_div2.html")
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
        br.open(file_="./tests/functions/remove_meta_info.html")
        self.assertTrue("bbbb" not in br.text)
        self.assertTrue("bbbb" not in br.html)
        self.assertOk(len(br.text.replace('\n', '')), 1400, delta=10)

    def test_article_html5_tag(self):
        br = Briticle()
        br.open(file_="./tests/functions/article_html5_tag.html")
        self.assertTrue("bbbb" not in br.text)
        self.assertTrue("bbbb" not in br.html)
        self.assertOk(len(br.text.replace('\n', '')), 1400, delta=10)

    def test_search_divs_with_h1(self):
        br = Briticle()
        br.open(file_="./tests/functions/divs_with_h1_1.html")
        self.assertTrue("bbbb" not in br.text)
        self.assertTrue("bbbb" not in br.html)
        self.assertOk(len(br.text.replace('\n', '')), 1400, delta=10)
        br = Briticle()
        br.open(file_="./tests/functions/divs_with_h1_2.html")
        self.assertTrue("bbbb" not in br.text)
        self.assertTrue("bbbb" not in br.html)
        self.assertOk(len(br.text.replace('\n', '')), 2800, delta=10)

    def test_search_p_biggest_parent(self):
        br = Briticle()
        br.open(file_="./tests/functions/p_biggest_parent.html")
        self.assertTrue("bbbb" not in br.text)
        self.assertTrue("bbbb" not in br.html)
        self.assertOk(len(br.text.replace('\n', '')), 1400, delta=10)

    def test_search_divs_with_p(self):
        br = Briticle()
        br.open(file_="./tests/functions/divs_with_p.html")
        self.assertTrue("bbbb" not in br.text)
        self.assertTrue("bbbb" not in br.html)
        self.assertOk(len(br.text.replace('\n', '')), 1400, delta=10)


if __name__ == "__main__":
    unittest.main()
