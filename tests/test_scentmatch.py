import unittest
from scentmatch.core import load_perfumes, score, rank, partition
from scentmatch.execution import execute
from scentmatch.distributed import execute_distributed

class Tests(unittest.TestCase):
    def setUp(self):
        self.data=load_perfumes()
        self.notes=['baunilha','lavanda','ambar']
    def test_score(self):
        self.assertEqual(score({'notas':['baunilha','ambar']},self.notes),66.67)
    def test_modes(self):
        baseline,_=execute(self.data,self.notes,'sequential')
        for mode in ('threading','multiprocessing'):
            result,_=execute(self.data,self.notes,mode,2)
            self.assertEqual(baseline,result)
    def test_partition(self):
        chunks=partition(self.data,3)
        self.assertEqual(sum(map(len,chunks)),len(self.data))
    def test_fallback(self):
        baseline,_=execute(self.data,self.notes,'sequential')
        result,_,recovered=execute_distributed(self.data,self.notes,[('127.0.0.1',1)],timeout=0.3)
        self.assertEqual(baseline,result)
        self.assertEqual(len(recovered),1)

if __name__=='__main__': unittest.main()
