#encoding=UTF8
import re
import unittest
from briticle import Briticle

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

if __name__ == "__main__":
    unittest.main()
