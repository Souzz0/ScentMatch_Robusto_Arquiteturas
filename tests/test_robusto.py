import unittest
from scentmatch.catalog import generate_catalog
from scentmatch.execution import execute
from scentmatch.core import analyze_batch

class RobustTests(unittest.TestCase):
    def test_reproducible(self):
        self.assertEqual(generate_catalog(30),generate_catalog(30))
    def test_notes(self):
        self.assertTrue(all(6<=len(x['notas'])<=12 for x in generate_catalog(100)))
    def test_modes(self):
        data=generate_catalog(80);notes=['lavanda','baunilha']
        baseline,_=execute(data,notes,'sequential',effort=70)
        for mode in ['threading','multiprocessing']:
            actual,_=execute(data,notes,mode,2,effort=70)
            self.assertEqual(baseline,actual)
    def test_effort(self):
        p=generate_catalog(2)
        self.assertNotEqual(analyze_batch(p,['baunilha'],1)[0]['assinatura'],analyze_batch(p,['baunilha'],50)[0]['assinatura'])
if __name__=='__main__':unittest.main()
