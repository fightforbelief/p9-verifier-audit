import itertools
import unittest
from functools import lru_cache
from fractions import Fraction
from math import comb
from audit import interval
from adjudication import upgrade, error_upper


class TranscriptTests(unittest.TestCase):
    def test_sequential_decision_tree(self):
        weights = (12,-8,7,-3,2)
        for observed in itertools.product((0,1), repeat=len(weights)):
            for e in range(3):
                possible = tuple(y for y in itertools.product((0,1), repeat=len(weights))
                                 if sum(a!=b for a,b in zip(y,observed))<=e)
                def width(truths):
                    vals=[sum(w*z for w,z in zip(weights,y)) for y in truths]
                    return max(vals)-min(vals)

                @lru_cache(None)
                def best(truths, ids, h):
                    if not h:
                        return width(truths)
                    return min(max(best(branch,tuple(j for j in ids if j!=i),h-1)
                                   for z in (0,1) if (branch:=tuple(y for y in truths if y[i]==z)))
                               for i in ids)

                for h in (0,1,2,3):
                    chosen=upgrade(list(zip(weights,observed)),h,e)
                    matching=tuple(y for y in possible if all(y[i]==observed[i] for i in chosen))
                    self.assertEqual(width(matching),best(possible,tuple(range(len(weights))),h))
                    self.assertEqual(len(set(chosen)),h)

    def test_exact_coverage(self):
        for m in range(1,18):
            for s in range(m+1):
                for total in range(m+1):
                    failure=Fraction(0)
                    for k in range(max(0,s-m+total),min(total,s)+1):
                        if error_upper(m,s,k,8)<total:
                            failure+=Fraction(comb(total,k)*comb(m-total,s-k),comb(m,s))
                    self.assertLessEqual(failure,Fraction(1,8))

    def test_grader_scope(self):
        from grader_replay import grades
        self.assertEqual(grades(r"\frac{2}{4}","0.5"),(False,True))
        self.assertEqual(grades(" 2 ","2"),(True,True))
        for ans,ref in [("1/0","0"),("50%",".5"),("x+x","2x"),("","")]:
            self.assertEqual(grades(ans,ref),(False,False))
