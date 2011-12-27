#encoding=UTF8
import re
import unittest
from briticle import Briticle, IMAGE_TAG

OFF_SETS = 20

class TestBriticle(unittest.TestCase):
    def testMitnkCom1(self):
        br = Briticle()
        br.open(file_="./tests/mitnk.com1.html")
        self.assertEqual(br.title, u"Linux_cut")
        self.assertTrue(u"列出系统所有用户" in br.content)
        self.assertTrue(u'cat /etc/passwd | cut -d ":" -f 1' in br.content)

    def testMitnkCom2(self):
        br = Briticle()
        br.open(file_="./tests/mitnk.com2.html")
        self.assertEqual(br.title, u"KISS")
        c = re.sub(r'\n', '', br.content)
        self.assertTrue(abs(len(c) - 2127) < OFF_SETS)

    def testWordPress(self):
        br = Briticle()
        br.open(file_="./tests/lixiaolai.com1.html")
        c = re.sub(r'\n', '', br.content).replace(IMAGE_TAG, "")
        self.assertTrue(abs(len(c) - 875) < OFF_SETS)

    def testTheNextWeb(self):
        br = Briticle()
        br.open(file_="./tests/thenextweb.com.html")
        c = re.sub(r'\n', '', br.content).replace(IMAGE_TAG, "")
        self.assertTrue(abs(len(c) - 1440) < OFF_SETS)

    def testGitHubProjectPage(self):
        br = Briticle()
        br.open(file_="./tests/github_project.html")
        c = re.sub(r'\n', '', br.content).replace(IMAGE_TAG, "")
        self.assertTrue(abs(len(c) - 1317) < OFF_SETS)

    def testClassContent(self):
        br = Briticle()
        br.open(file_="./tests/petzl.com.html")
        c = re.sub(r'\n', '', br.content).replace(IMAGE_TAG, "")
        self.assertTrue(abs(len(c) - 3761) < OFF_SETS)


if __name__ == "__main__":
    unittest.main()
